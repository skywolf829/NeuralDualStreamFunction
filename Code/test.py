from __future__ import absolute_import, division, print_function
import argparse
import os
from Other.utility_functions import nc_to_tensor
from Models.models import load_model
from Models.options import *
from Datasets.datasets import Dataset
import torch

project_folder_path = os.path.dirname(os.path.abspath(__file__))
project_folder_path = os.path.join(project_folder_path, "..")
data_folder = os.path.join(project_folder_path, "Data")
output_folder = os.path.join(project_folder_path, "Output")
save_folder = os.path.join(project_folder_path, "SavedModels")

def model_reconstruction(model, dataset, opt):
    grid = list(dataset.data.shape[2:])
    if("dsfm" in opt['training_mode']): 
        grads_f = model.sample_grad_grid(grid, output_dim=0, 
                                        max_points=10000)
        grads_g = model.sample_grad_grid(grid, output_dim=1, 
                                        max_points=10000)
        grads_f = grads_f.permute(3, 0, 1, 2).unsqueeze(0)
        grads_g = grads_g.permute(3, 0, 1, 2).unsqueeze(0)
        with torch.no_grad():
            m = model.sample_grid(grid, max_points=100000)[...,2:3]
            m = m.permute(3, 0, 1, 2).unsqueeze(0)
        result = torch.cross(grads_f, grads_g, dim=1)
        result /= (result.norm(dim=1) + 1e-8)
        result *= m
        
    elif("uvw" in opt['training_mode']):
        with torch.no_grad():
            result = model.sample_grid(grid, max_points = 100000)
            result = result.permute(3, 0, 1, 2).unsqueeze(0)
            
    print(result.shape)   

def perform_tests(model, data, tests, opt):
    if("reconstruction" in tests):
        if(opt['training_mode'] == "dsfm_any" or
           opt['training_mode'] == "dsfm_parallel" or
           opt['training_mode'] == "dsfm_direction" or
           opt['training_mode'] == "uvw" or 
           opt['training_mode'] == "uvwf_any" or
           opt['training_mode'] == "uvwf_parallel" or
           opt['training_mode'] == "uvwf_direction" or
           opt['training_mode'] == "hhd"):
            reconstructed = model_reconstruction(model, data, opt)
        else:
            print(f"Training mode {opt['training_mode']} does not support the reconstruction task")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Evaluate a model on some tests')

    parser.add_argument('--load_from',default=None,type=str,help="Model name to load")
    parser.add_argument('--tests_to_run',default=None,type=str,
                        help="A set of tests to run, separated by commas")
    parser.add_argument('--device',default=None,type=str,
                        help="Device to load model to")
    parser.add_argument('--data_device',default=None,type=str,
                        help="Device to load data to")
    args = vars(parser.parse_args())

    project_folder_path = os.path.dirname(os.path.abspath(__file__))
    project_folder_path = os.path.join(project_folder_path, "..")
    data_folder = os.path.join(project_folder_path, "Data")
    output_folder = os.path.join(project_folder_path, "Output")
    save_folder = os.path.join(project_folder_path, "SavedModels")
    
    tests_to_run = args['tests_to_run'].split(',')
    
    # Load the model
    opt = load_options(os.path.join(save_folder, args['load_from']))
    opt['device'] = args['device']
    opt['data_device'] = args['data_device']
    model = load_model(opt, args['device']).to(args['device'])
    model.eval()
    
    # Load the reference data
    data = Dataset(opt)
    
    # Perform tests
    perform_tests(model, data, tests_to_run, opt)
    
        
    
        



        

