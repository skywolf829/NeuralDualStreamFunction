from __future__ import absolute_import, division, print_function
import argparse
from datasets import Dataset
import datetime
from utility_functions import str2bool, PSNR, make_coord_grid, tensor_to_cdf, ssim3D
from models import load_model, save_model, ImplicitModel
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP
import time
import os
import h5py
from options import *
from torch.utils.tensorboard import SummaryWriter
import torch.multiprocessing as mp

project_folder_path = os.path.dirname(os.path.abspath(__file__))
project_folder_path = os.path.join(project_folder_path, "..")
data_folder = os.path.join(project_folder_path, "Data")
output_folder = os.path.join(project_folder_path, "Output")
save_folder = os.path.join(project_folder_path, "SavedModels")



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train on an input that is 2D')

    parser.add_argument('--load_from',default=None,type=str)
    parser.add_argument('--supersample',default=None,type=float)
    parser.add_argument('--supersample_psnr',default=None,type=str)
    parser.add_argument('--supersample_gradient',default=None,type=float)
    parser.add_argument('--normal_field',default=None,type=str2bool)
    parser.add_argument('--implicit_jacobian',default=None,type=str2bool)
    parser.add_argument('--jacobian_discrete',default=None,type=str2bool)
    parser.add_argument('--cdf',default=None,type=str2bool)
    parser.add_argument('--grad_cdf',default=None,type=str2bool)
    parser.add_argument('--device',default="cuda:0",type=str)

    args = vars(parser.parse_args())

    project_folder_path = os.path.dirname(os.path.abspath(__file__))
    project_folder_path = os.path.join(project_folder_path, "..")
    data_folder = os.path.join(project_folder_path, "Data")
    output_folder = os.path.join(project_folder_path, "Output")
    save_folder = os.path.join(project_folder_path, "SavedModels")


    if(args['load_from'] is None):
        print("Must load a model")
        quit()
         
    opt = load_options(os.path.join(save_folder, args["load_from"]))
    opt["device"] = args["device"]
    opt['data_device'] = args['device']
    opt["save_name"] = args["load_from"]
    for k in args.keys():
        if args[k] is not None:
            opt[k] = args[k]
    dataset = Dataset(opt)
    model = load_model(opt, opt['device'])
    model = model.to(opt['device'])

    print(dataset.data.min())
    print(dataset.data.mean())
    print(dataset.data.max())

    writer = SummaryWriter(os.path.join('tensorboard',opt['save_name']))

    if(args['supersample_psnr'] is not None):
        original_volume = h5py.File(os.path.join(data_folder, args['supersample_psnr']), 'r')['data']
        original_volume = torch.tensor(original_volume).to(opt['device']).unsqueeze(0)
        print(original_volume.shape)
        grid = list(original_volume.shape[2:])
        with torch.no_grad():
            supersampled_volume = model.sample_grid(grid)
            if(len(grid) == 3):
                supersampled_volume = supersampled_volume.permute(3, 0, 1, 2).unsqueeze(0)
            else:
                supersampled_volume = supersampled_volume.permute(2, 0, 1).unsqueeze(0)
            tensor_to_cdf(supersampled_volume, os.path.join(output_folder, opt['save_name']+"_supersampled.cdf"))


            p_model = PSNR(original_volume, supersampled_volume, 
                range=original_volume.max()-original_volume.min()).item()
            s_model = ssim3D(original_volume, supersampled_volume).item()
            print("Neural network supersampling PSNR/SSIM: %0.03f/%0.05f" % (p_model, s_model))

            ss_interp_volume = model.sample_grid(list(dataset.data.shape[2:]))
            if(len(grid) == 3):
                ss_interp_volume = ss_interp_volume.permute(3, 0, 1, 2).unsqueeze(0)
            else:
                ss_interp_volume = ss_interp_volume.permute(2, 0, 1).unsqueeze(0)
            ss_interp_volume = F.interpolate(ss_interp_volume, size=original_volume.shape[2:],
                align_corners=False, mode='trilinear' if len(original_volume.shape) == 5 else 'bilinear')

            tensor_to_cdf(ss_interp_volume, os.path.join(output_folder, opt['save_name']+"_with_interpolation.cdf"))
            p_ss_interp = PSNR(original_volume, ss_interp_volume,
                range=original_volume.max()-original_volume.min()).item()
            s_ss_interp = ssim3D(original_volume, ss_interp_volume).item()
            print("Network + interp supersampling PSNR/SSIM: %0.03f/%0.05f" % (p_ss_interp, s_ss_interp))

            interpolated_volume = F.interpolate(dataset.data.to(opt['device']), size=original_volume.shape[2:],
                align_corners=False, mode='trilinear' if len(original_volume.shape) == 5 else 'bilinear')

            tensor_to_cdf(interpolated_volume, os.path.join(output_folder, opt['save_name']+"_interpolated.cdf"))
            p_interp = PSNR(original_volume, interpolated_volume,
                range=original_volume.max()-original_volume.min()).item()
            s_interp = ssim3D(original_volume, interpolated_volume).item()
            print("Interpolation supersampling PSNR/SSIM: %0.03f/%0.05f" % (p_interp, s_interp))
            
            tensor_to_cdf(original_volume, os.path.join(output_folder, args['supersample_psnr']+'.cdf'))

    if(args['supersample'] is not None):
        grid = list(dataset.data.shape[2:])
        for i in range(len(grid)):
            grid[i] *= args['supersample']
            grid[i] = int(grid[i])
        with torch.no_grad():
            img = model.sample_grid(grid)
        print(img.min())
        print(img.mean())
        print(img.max())
        print(img.shape)
        writer.add_image('Supersample x'+str(args['supersample']), 
            img.clamp(dataset.min(), dataset.max()), 0, dataformats='WHC')
        
    if(args['supersample_gradient'] is not None):
        grid = list(dataset.data.shape[2:])
        for i in range(len(grid)):
            grid[i] *= args['supersample_gradient']
            grid[i] = int(grid[i])
        
        grad_img = model.sample_grad_grid(grid)
        
        for output_index in range(len(grad_img)):
            for input_index in range(grad_img[output_index].shape[-1]):
                grad_img[output_index][...,input_index] -= \
                    grad_img[output_index][...,input_index].min()
                grad_img[output_index][...,input_index] /= \
                    grad_img[output_index][...,input_index].max()
                                                
                writer.add_image('Supersample gradient_outputdim'+str(output_index)+\
                    "_wrt_inpudim_"+str(input_index), 
                    grad_img[output_index][...,input_index:input_index+1].clamp(0, 1), 
                    0, dataformats='WHC')
    
    if(args['normal_field'] is not None):
        grid = list(dataset.data.shape[2:])
        
        with torch.no_grad():
            vector_field = model.sample_grid(grid)
            print(vector_field.shape)

        jacobian = model.sample_grad_grid(grid)
        
        with torch.no_grad():
            jacobian = torch.cat(jacobian, dim=1)
            print(jacobian.shape)
            
            normal_field = torch.matmul(jacobian, vector_field)
            print(normal_field.shape)

    if(args['implicit_jacobian'] is not None):
        grid = list(dataset.data.shape[2:])
        coord_grid = make_coord_grid(grid, model.opt['device'], False)
        coord_grid_shape = list(coord_grid.shape)
        coord_grid = coord_grid.view(-1, coord_grid.shape[-1]).requires_grad_(True)       

        output_shape = list(coord_grid.shape)
        output_shape[-1] = model.opt['n_dims']
        print("Output shape")
        print(output_shape)
        output_grad = torch.empty(output_shape, 
            dtype=torch.float32, device=model.opt['device'], 
            requires_grad=False)

        output_shape.append(3)

        output_jacobian = torch.empty(output_shape, 
            dtype=torch.float32, device=model.opt['device'], 
            requires_grad=False)

        max_points = 1000
        for start in range(0, coord_grid.shape[0], max_points):
            points = coord_grid[start:min(start+max_points, coord_grid.shape[0])].clone()
            vals = model.net(
                points)
            grad = torch.autograd.grad(outputs=vals, 
                inputs=points, 
                grad_outputs=torch.ones_like(vals),
                create_graph=True)[0]

            output_grad[start:min(start+max_points, coord_grid.shape[0])] = grad.clone().detach()
                
            for dim in range(grad.shape[1]):
                grad2 = torch.autograd.grad(outputs=grad[:,dim:dim+1],
                    inputs=points,
                    grad_outputs=torch.ones_like(grad[:,dim:dim+1]),
                    retain_graph=True)[0]
                output_jacobian[start:min(start+max_points, coord_grid.shape[0]), dim] = \
                    grad2.detach()
            #print(grad2[0][start:min(start+max_points, coord_grid.shape[0])].shape)

        print(output_grad.shape)
        print(output_jacobian.shape)

        n = torch.bmm(output_jacobian.transpose(1, 2), output_grad.unsqueeze(-1))[...,0]
        n /= torch.norm(n, dim=1, keepdim=True)
        b = torch.cross(n, output_grad, dim=1)
        b /= torch.norm(b, dim=1, keepdim=True)
        print(n.shape)
        print(b.shape)


        reconstructed_vf = output_grad.reshape(coord_grid_shape)
        if(len(grid) == 3):
            reconstructed_vf = reconstructed_vf.permute(3, 0, 1, 2).unsqueeze(0)
        else:
            reconstructed_vf = reconstructed_vf.permute(2, 0, 1).unsqueeze(0)

        reconstructed_bvf = b.reshape(coord_grid_shape)
        reconstructed_nvf = n.reshape(coord_grid_shape)
        if(len(grid) == 3):
            reconstructed_bvf = reconstructed_bvf.permute(3, 0, 1, 2).unsqueeze(0)
            reconstructed_nvf = reconstructed_nvf.permute(3, 0, 1, 2).unsqueeze(0)
        else:
            reconstructed_bvf = reconstructed_bvf.permute(2, 0, 1).unsqueeze(0)
            reconstructed_nvf = reconstructed_nvf.permute(3, 0, 1, 2).unsqueeze(0)
        
        tensor_to_cdf(reconstructed_bvf, 
            os.path.join(output_folder, opt['save_name']+"_binormal_reconstructed.cdf"))

        tensor_to_cdf(reconstructed_nvf, 
            os.path.join(output_folder, opt['save_name']+"_normal_reconstructed.cdf"))

    if(args['jacobian_discrete'] is not None):
        grid = list(dataset.data.shape[2:])
        coord_grid = make_coord_grid(grid, model.opt['device'], False)
        coord_grid_shape = list(coord_grid.shape)
        jacobian_shape = list(coord_grid.shape)
        jacobian_shape.append(3)
        coord_grid = coord_grid.view(-1, coord_grid.shape[-1]).requires_grad_(True)       

        output_shape = list(coord_grid.shape)
        output_shape[-1] = model.opt['n_dims']
        print("Output shape")
        print(output_shape)
        output_grad = torch.empty(output_shape, 
            dtype=torch.float32, device=model.opt['device'], 
            requires_grad=False)

        output_shape.append(3)

        output_jacobian = torch.empty(jacobian_shape, 
            dtype=torch.float32, device=model.opt['device'], 
            requires_grad=False).permute(3, 4, 0, 1, 2).unsqueeze(0)

        print("Jacobian shape")
        print(output_jacobian.shape)
        max_points = 1000
        for start in range(0, coord_grid.shape[0], max_points):
            points = coord_grid[start:min(start+max_points, coord_grid.shape[0])].clone()
            vals = model.net(
                points)
            grad = torch.autograd.grad(outputs=vals, 
                inputs=points, 
                grad_outputs=torch.ones_like(vals),
                create_graph=True)[0]

            output_grad[start:min(start+max_points, coord_grid.shape[0])] = grad.clone().detach()
        

        reconstructed_vf = output_grad.reshape(coord_grid_shape)
        if(len(grid) == 3):
            reconstructed_vf = reconstructed_vf.permute(3, 0, 1, 2).unsqueeze(0)
        else:
            reconstructed_vf = reconstructed_vf.permute(2, 0, 1).unsqueeze(0)
        print("reconstructed vf shape")
        print(reconstructed_vf.shape)

        z_kernel = torch.zeros([3, 3, 3, 3, 3], device=opt['device'])
        z_kernel[:, :, 0, 1, 1] = -0.5
        z_kernel[:, :, 2, 1, 1] = 0.5
        y_kernel = torch.zeros([3, 3, 3, 3, 3], device=opt['device'])
        y_kernel[:, :, 1, 0, 1] = -0.5
        y_kernel[:, :, 1, 2, 1] = 0.5
        x_kernel = torch.zeros([3, 3, 3, 3, 3], device=opt['device'])
        x_kernel[:, :, 1, 1, 0] = -0.5
        x_kernel[:, :, 1, 1, 2] = 0.5

        output_jacobian[0,0] = F.conv3d(reconstructed_vf, z_kernel, padding=1)
        output_jacobian[0,1] = F.conv3d(reconstructed_vf, y_kernel, padding=1)
        output_jacobian[0,2] = F.conv3d(reconstructed_vf, x_kernel, padding=1)

        output_jacobian = output_jacobian[0].permute(2, 3, 4, 0, 1).flatten(0, 2)
        print(output_jacobian.shape)
        reconstructed_vf = reconstructed_vf[0].permute(1, 2, 3, 0).flatten(0, 2)
        print(reconstructed_vf.shape)

        n = torch.bmm(output_jacobian, reconstructed_vf.unsqueeze(-1))[...,0]
        n /= torch.norm(n, dim=1, keepdim=True)
        b = torch.cross(n, output_grad, dim=1)
        b /= torch.norm(b, dim=1, keepdim=True)
        print(n.shape)
        print(b.shape)


        

        reconstructed_bvf = b.reshape(coord_grid_shape)
        reconstructed_nvf = n.reshape(coord_grid_shape)
        if(len(grid) == 3):
            reconstructed_bvf = reconstructed_bvf.permute(3, 0, 1, 2).unsqueeze(0)
            reconstructed_nvf = reconstructed_nvf.permute(3, 0, 1, 2).unsqueeze(0)
        else:
            reconstructed_bvf = reconstructed_bvf.permute(2, 0, 1).unsqueeze(0)
            reconstructed_nvf = reconstructed_nvf.permute(3, 0, 1, 2).unsqueeze(0)
        
        tensor_to_cdf(reconstructed_bvf, 
            os.path.join(output_folder, opt['save_name']+"_binormal_discrete.cdf"))

        tensor_to_cdf(reconstructed_nvf, 
            os.path.join(output_folder, opt['save_name']+"_normal_discrete.cdf"))

    if(args['cdf'] is not None):
        grid = list(dataset.data.shape[2:])
        with torch.no_grad():
            reconstructed_volume = model.sample_grid(grid)
        if(len(grid) == 3):
            reconstructed_volume = reconstructed_volume.permute(3, 0, 1, 2).unsqueeze(0)
        else:
            reconstructed_volume = reconstructed_volume.permute(2, 0, 1).unsqueeze(0)
        
        #p_ss_interp = PSNR(dataset.data, reconstructed_volume,
            #range=dataset.max()-dataset.min()).item()
        #s_ss_interp = ssim3D(dataset.data, reconstructed_volume).item()
        #print("Reconstructed PSNR/SSIM: %0.03f/%0.05f" % (p_ss_interp, s_ss_interp))

        tensor_to_cdf(reconstructed_volume, 
            os.path.join(output_folder, opt['save_name']+"_reconstructed.cdf"))
        tensor_to_cdf(dataset.data, 
            os.path.join(output_folder, opt['save_name']+"_original.cdf"))

    if(args['grad_cdf'] is not None):
        grid = list(dataset.data.shape[2:])
        reconstructed_volume = model.sample_grad_grid(grid)
        if(len(grid) == 3):
            reconstructed_volume = reconstructed_volume.permute(3, 0, 1, 2).unsqueeze(0)
        else:
            reconstructed_volume = reconstructed_volume.permute(2, 0, 1).unsqueeze(0)
        
        #p_ss_interp = PSNR(dataset.data, reconstructed_volume,
            #range=dataset.max()-dataset.min()).item()
        #s_ss_interp = ssim3D(dataset.data, reconstructed_volume).item()
        #print("Reconstructed PSNR/SSIM: %0.03f/%0.05f" % (p_ss_interp, s_ss_interp))

        tensor_to_cdf(reconstructed_volume, 
            os.path.join(output_folder, opt['save_name']+"_grad_reconstructed.cdf"))
        tensor_to_cdf(dataset.data, 
            os.path.join(output_folder, opt['save_name']+"_original.cdf"))

    writer.close()
        



        

