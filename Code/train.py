from __future__ import absolute_import, division, print_function
import argparse
from inspect import trace
from Datasets.datasets import get_dataset
import datetime
from Other.utility_functions import str2bool, particle_tracing
from Models.models import load_model, create_model, save_model
import torch
import torch.optim as optim
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
import time
import os
from Models.options import *
from torch.utils.tensorboard import SummaryWriter
import torch.multiprocessing as mp
from Models.losses import *
import shutil

project_folder_path = os.path.dirname(os.path.abspath(__file__))
project_folder_path = os.path.join(project_folder_path, "..")
data_folder = os.path.join(project_folder_path, "Data")
output_folder = os.path.join(project_folder_path, "Output")
save_folder = os.path.join(project_folder_path, "SavedModels")

def log_to_writer(iteration, losses, writer, opt):
    with torch.no_grad():   
        print_str = f"Iteration {iteration}/{opt['iterations']}, "
        for key in losses.keys():    
            print_str = print_str + str(key) + f": {losses[key].item() : 0.05f} " 
            writer.add_scalar(str(key), losses[key].item(), iteration)
        print(print_str)
        GBytes = (torch.cuda.max_memory_allocated(device=opt['device']) \
            / (1024**3))
        writer.add_scalar('GPU memory (GB)', GBytes, iteration)

def log_image(model, dataset, grid_to_sample, writer, iteration):
    with torch.no_grad():
        img = model.sample_grid_for_image(grid_to_sample)
        print("img shape: " + str(img.shape))
        if(dataset.min() < 0 or dataset.max() > 1.0):
            img -= dataset.min()
            img /= (dataset.max() - dataset.min())
        writer.add_image('Reconstruction', img.clamp(0, 1), 
            iteration, dataformats='HWC')

def log_grad_image(model, grid_to_sample, writer, iteration):
    grad_img = model.sample_grad_grid_for_image(grid_to_sample)
    for output_index in range(len(grad_img)):
        for input_index in range(grad_img[output_index].shape[-1]):
            grad_img[output_index][...,input_index] -= \
                grad_img[output_index][...,input_index].min()
            grad_img[output_index][...,input_index] /= \
                grad_img[output_index][...,input_index].max()

            writer.add_image('Gradient_outputdim'+str(output_index)+\
                "_wrt_inpudim_"+str(input_index), 
                grad_img[output_index][...,input_index:input_index+1].clamp(0, 1), 
                iteration, dataformats='HWC')

def logging(writer, iteration, losses):
    if(iteration % 5 == 0):
        log_to_writer(iteration, losses, writer, opt)
                    
def train(rank, model, dataset, opt):
    print("Training on device " + str(rank))
    if(opt['train_distributed']):        
        print("Initializing process group.")
        opt['device'] = "cuda:" + str(rank)
        dist.init_process_group(                                   
            backend='nccl',                                         
            init_method='env://',                                   
            world_size=opt['gpus_per_node'],                              
            rank=rank                                               
        )  

    if(opt['train_distributed']):
        model = DDP(model, device_ids=[rank])
    else:
        model = model.to(opt['device'])
        
    print("Training on %s" % (opt["device"]), 
        os.path.join(save_folder, opt["save_name"]))

    if(opt['model'] == "grid"):
        optimizer = optim.SGD(model.parameters(), lr=opt['lr'])
        scheduler = None
    else:
        optimizer = optim.Adam(model.parameters(), lr=opt["lr"],
            betas=[opt['beta_1'], opt['beta_2']]) 
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, 
            step_size=opt['iterations']//3, gamma=0.1)

    if((rank == 0 and opt['train_distributed']) or not opt['train_distributed']):
        if(os.path.exists(os.path.join(project_folder_path, "tensorboard", opt['save_name']))):
            shutil.rmtree(os.path.join(project_folder_path, "tensorboard", opt['save_name']))
        writer = SummaryWriter(os.path.join('tensorboard',opt['save_name']))
        gt_img = dataset.get_2D_slice()
        gt_img -= dataset.min()
        gt_img /= (dataset.max() - dataset.min())
        writer.add_image("Ground Truth", gt_img, 0, dataformats="CHW")
    
    model.train(True)

    loss_func = get_loss_func(opt)

    for iteration in range(0, opt['iterations']):
        opt['iteration_number'] = iteration

        optimizer.zero_grad()
        data = dataset.get_random_points(opt['points_per_iteration'])
        for k in data.keys():
            data[k] = data[k].to(opt['device'])
        if("any" in opt['training_mode'] or "direction" in opt['training_mode']
           or "parallel" in opt['training_mode'] or opt['training_mode'] == "hhd" or 
           "PSF" in opt['training_mode']):
            data['inputs'] = data['inputs'].requires_grad_(True)
        
        if(opt['model'] == "grid"):
            model_output = model.forward_grad(data['inputs'])
        else:
            model_output = model(data['inputs'])
        losses = {}
        loss = loss_func(model_output, data)
        losses['fitting_loss'] = loss
        
        if(opt['seeding_points'] is not None):
            model_seed_output = model(data['seeds'])
            s_l = seeding_loss(model_seed_output) * 10
            loss = loss + s_l
            losses['seeding_curve'] = s_l
        if(opt['streamline_loss'] and iteration > opt['iterations'] *(2/3)):
            traces = particle_tracing(dataset.data,
            data['inputs'][0:100], steps=500, h=0.75, 
            align_corners=opt['align_corners'])
            
            trace_shape = list(traces.shape)
            trace_shape[-1] = 1
            model_trace_output = model(traces.reshape(-1, 3))
            model_trace_output = model_trace_output.reshape(trace_shape)
            #print(f"model_trace_output {model_trace_output.shape}")
            #print(f"model_trace_output {model_trace_output[0:10,0,0]}")

            trace_mean = model_trace_output.mean(dim=0)
            trace_mean = trace_mean.unsqueeze(0).repeat(trace_shape[0], 1, 1)
            #print(f"actual means {trace_mean[0:10,0,0]}")
            
            model_trace_output = torch.abs(model_trace_output - trace_mean)
            #print(f"means {model_trace_output.shape}")
            #print(f"means {model_trace_output[0:10, 0, 0]}")   
            #print(f"diff means {model_trace_output.mean(dim=0).shape}")      
            tracing_loss = model_trace_output.mean() * 50
            loss = loss + tracing_loss
            losses['tracing_loss'] = tracing_loss

        loss.backward()
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        
        if((rank == 0 and opt['train_distributed']) or not opt['train_distributed']):
            logging(writer, iteration, losses)
        opt['iteration_number'] = iteration
    
    if((rank == 0 and opt['train_distributed']) or not opt['train_distributed']):
        writer.close()

    save_model(model, opt)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Trains an implicit model on data.')

    parser.add_argument('--n_dims',default=None,type=int,
        help='Number of dimensions in the data')
    parser.add_argument('--n_outputs',default=None,type=int,
        help='Number of output channels for the data (ex. 1 for scalar field, 3 for image or vector field)')
    parser.add_argument('--model',default=None,type=str,
        help='The model architecture used for training')
    parser.add_argument('--training_mode',default=None,type=str,
        help='Training mode chooses the loss function for the model, as ' + \
        'well as assumes what each output from the model means.'
    )
    parser.add_argument('--device',default=None, type=str,
        help='Which device to train on')
    parser.add_argument('--data_device',default=None,type=str,
        help='Which device to keep the data on')
    
    parser.add_argument('--data',default=None,type=str,
        help='Data file name')
    parser.add_argument('--interpolate',default=None,type=str2bool,
        help='Interpolate points during training')
    parser.add_argument('--align_corners',default=None,type=str2bool,
        help='Aligns corners in implicit model.')
    parser.add_argument('--seeding_points',default=None,type=str,
        help='Seeding points file')
    parser.add_argument('--streamline_loss',default=None,type=str2bool,
        help='Streamline regularization loss enabled or not')
    parser.add_argument('--save_name',default=None,type=str,
        help='Save name for the model')
    
    parser.add_argument('--n_layers',default=None,type=int,
        help='Number of layers in the model')
    parser.add_argument('--nodes_per_layer',default=None,type=int,
        help='Nodes per layer in the model')    

    parser.add_argument('--n_features',default=None,type=int,
        help='Number of features in the feature grid')    
    parser.add_argument('--num_positional_encoding_terms',default=None,type=int,
        help='Number of fourier features')
    parser.add_argument('--grid_size',default=None,type=int,
        help='Feature grid size, or grid size for direct solving')    
    
    parser.add_argument('--train_distributed',default=None,type=str2bool,
        help='Train on multiple GPUs')
    parser.add_argument('--gpus_per_node',default=None, type=int,
        help='GPUs per node when training distributed')
    parser.add_argument('--num_nodes',default=None, type=int,
        help='Number of nodes')
    parser.add_argument('--ranking',default=None, type=int,
        help='Not used.')

    parser.add_argument('--iterations',default=None, type=int,
        help='Number of iterations to train')
    parser.add_argument('--points_per_iteration',default=None, type=int,
        help='Number of points to sample per training loop update')
    parser.add_argument('--lr',default=None, type=float,
        help='Learning rate for the adam optimizer')
    parser.add_argument('--beta_1',default=None, type=float,
        help='Beta1 for the adam optimizer')
    parser.add_argument('--beta_2',default=None, type=float,
        help='Beta2 for the adam optimizer')

    parser.add_argument('--iteration_number',default=None, type=int,
        help="Not used.")
    parser.add_argument('--save_every',default=None, type=int,
        help='How often to save the model')
    parser.add_argument('--log_every',default=None, type=int,
        help='How often to log the loss')
    parser.add_argument('--load_from',default=None, type=str,
        help='Model to load to start training from')
    parser.add_argument('--log_image',default=None, type=str2bool,
        help='Whether or not to log an image. Slows down training.')
    parser.add_argument('--log_gradient',default=None, type=str2bool,
        help='Whether or not to log the gradient of the output. Slows down training.')


    args = vars(parser.parse_args())

    project_folder_path = os.path.dirname(os.path.abspath(__file__))
    project_folder_path = os.path.join(project_folder_path, "..")
    data_folder = os.path.join(project_folder_path, "Data")
    output_folder = os.path.join(project_folder_path, "Output")
    save_folder = os.path.join(project_folder_path, "SavedModels")

    torch.manual_seed(11235813)

    if(args['load_from'] is None):
        # Init models
        model = None
        opt = Options.get_default()

        # Read arguments and update our options
        for k in args.keys():
            if args[k] is not None:
                opt[k] = args[k]

        dataset = get_dataset(opt)
        model = create_model(opt)
    else:        
        opt = load_options(os.path.join(save_folder, args["load_from"]))
        opt["device"] = args["device"]
        opt["save_name"] = args["load_from"]
        for k in args.keys():
            if args[k] is not None:
                opt[k] = args[k]
        dataset = get_dataset(opt)
        model = load_model(opt, opt['device'])

    now = datetime.datetime.now()
    start_time = time.time()
    
       
    if(opt['train_distributed']):
        os.environ['MASTER_ADDR'] = '127.0.0.1'              
        os.environ['MASTER_PORT'] = '29500' 
        mp.spawn(train,
            args=(model, dataset, opt),
            nprocs=opt['gpus_per_node'],
            join=True)
    else:
        train(opt['device'], model, 
                dataset,opt)
        
    opt['iteration_number'] = 0
    save_model(model, opt)
    

