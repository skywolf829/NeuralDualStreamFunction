#!/bin/sh
cd /lus/theta-fs0/projects/DL4VIS/ImplicitStreamFunction

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 4 --nodes_per_layer 128 \
--save_name isotropic_coarse_sf_4x128 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:0 --data_device cuda:0 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 4 --nodes_per_layer 256 \
--save_name isotropic_coarse_sf_4x256 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:1 --data_device cuda:1 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 4 --nodes_per_layer 512 \
--save_name isotropic_coarse_sf_4x512 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:2 --data_device cuda:2 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 4 --nodes_per_layer 1024 \
--save_name isotropic_coarse_sf_4x1024 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:3 --data_device cuda:3 &


###########################################################

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 6 --nodes_per_layer 128 \
--save_name isotropic_coarse_sf_6x128 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:4 --data_device cuda:4 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 6 --nodes_per_layer 256 \
--save_name isotropic_coarse_sf_6x256 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:5 --data_device cuda:5 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 6 --nodes_per_layer 512 \
--save_name isotropic_coarse_sf_6x512 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:6 --data_device cuda:6 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 6 --nodes_per_layer 1024 \
--save_name isotropic_coarse_sf_6x1024 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:7 --data_device cuda:7


###########################################################

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 8 --nodes_per_layer 128 \
--save_name isotropic_coarse_sf_8x128 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:0 --data_device cuda:0 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 8 --nodes_per_layer 256 \
--save_name isotropic_coarse_sf_8x256 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:1 --data_device cuda:1 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 8 --nodes_per_layer 512 \
--save_name isotropic_coarse_sf_8x512 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:2 --data_device cuda:2 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 8 --nodes_per_layer 1024 \
--save_name isotropic_coarse_sf_8x1024 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:3 --data_device cuda:3 &


###########################################################

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 10 --nodes_per_layer 128 \
--save_name isotropic_coarse_sf_10x128 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:4 --data_device cuda:4 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 10 --nodes_per_layer 256 \
--save_name isotropic_coarse_sf_10x256 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:5 --data_device cuda:5 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 10 --nodes_per_layer 512 \
--save_name isotropic_coarse_sf_10x512 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:6 --data_device cuda:6 &

python -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name isotropic_coarse_mag.h5 \
--n_layers 10 --nodes_per_layer 1024 \
--save_name isotropic_coarse_sf_10x1024 \
--points_per_iteration 200000 \
--log_image false --log_gradient false \
--device cuda:7 --data_device cuda:7


###########################################################