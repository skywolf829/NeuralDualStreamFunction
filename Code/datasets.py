import os
import torch
import h5py
from utility_functions import make_coord_grid
import torch.nn.functional as F

project_folder_path = os.path.dirname(os.path.abspath(__file__))
project_folder_path = os.path.join(project_folder_path, "..")
data_folder = os.path.join(project_folder_path, "Data")
output_folder = os.path.join(project_folder_path, "Output")
save_folder = os.path.join(project_folder_path, "SavedModels")



class Dataset(torch.utils.data.Dataset):
    def __init__(self, opt):
        
        self.opt = opt
        self.min_ = None
        self.max_ = None

        folder_to_load = os.path.join(data_folder, self.opt['vector_field_name'])

        print("Initializing dataset - reading %s" % folder_to_load)
        
        f = h5py.File(folder_to_load, 'r')
        d = torch.tensor(f.get('data'))
        f.close()
        self.data = d
        self.data = self.data.to(self.opt['data_device']).unsqueeze(0)
        print("Data size: " + str(self.data.shape))

    def min(self):
        if self.min_ is not None:
            return self.min_
        else:
            self.min_ = self.data.min()
            return self.min_
    def max(self):
        if self.max_ is not None:
            return self.max_
        else:
            self.max_ = self.data.max()
            return self.max_

    def get_2D_slice(self):
        if(len(self.data.shape) == 4):
            return self.data[0]
        else:
            return self.data[0,:,int(self.data.shape[2]/2),:,:]

    def total_points(self):
        t = 1
        for i in range(2, len(self.data.shape)):
            t *= self.data.shape[i]
        return t

    def get_random_points(self, n_points):        
        if(self.opt['interpolate']):
            x = (torch.rand([1, n_points, len(self.data.shape[2:])], 
                device=self.data.device) - 0.5) * 2
            for _ in range(len(self.data.shape[2:])-1):
                x = x.unsqueeze(-2)
            y = F.grid_sample(self.data, 
                x, mode='bilinear', align_corners=False)
        else:
            x_dims = []
            if(n_points == self.total_points()):
                x = make_coord_grid(self.data.shape[2:], 
                    self.opt['device'], flatten=True).unsqueeze(0)
            else:
                for i in range(len(self.data.shape[2:])):
                    x = torch.randint(0, self.data.shape[2+i], [1, n_points, 1], 
                        dtype=torch.float32, device=self.opt['data_device'])
                    x += 0.5
                    x *= (2 / (self.data.shape[2+i]+1))
                    x -= 1
                    x_dims.append(x)
                x = torch.cat(x_dims, -1)
            for _ in range(len(self.data.shape[2:])-1):
                x = x.unsqueeze(-2)
            
            y = F.grid_sample(self.data, 
                x, mode='nearest', align_corners=False)
        
        x = x.squeeze()
        y = y.squeeze()
        if(len(y.shape) == 1):
            y = y.unsqueeze(0)        
        y = y.permute(1,0)

        return x, y