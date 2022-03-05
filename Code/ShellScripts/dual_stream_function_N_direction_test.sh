#!/bin/sh
cd /lus/theta-fs0/projects/DL4VIS/ImplicitStreamFunction

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name vortices.h5 \
--save_name N_direction_dual_streamfunction_vortices \
--n_layers 4 --nodes_per_layer 128 \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function N_direction \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:0 --data_device cuda:0 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name flow_past_cylinder.h5 \
--save_name N_direction_dual_streamfunction_flow_past_cylinder \
--n_layers 4 --nodes_per_layer 128 \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function N_direction \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:1 --data_device cuda:1 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name ABC_flow.h5 \
--save_name N_direction_dual_streamfunction_ABC_flow \
--n_layers 4 --nodes_per_layer 128 \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function N_direction \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:2 --data_device cuda:2 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name N_direction_dual_streamfunction_tornado3d \
--n_layers 4 --nodes_per_layer 128 \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function N_direction \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:3 --data_device cuda:3 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name N_direction_dual_streamfunction_isabel \
--n_layers 4 --nodes_per_layer 128 \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function N_direction \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:4 --data_device cuda:4 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name N_direction_dual_streamfunction_plume \
--n_layers 4 --nodes_per_layer 128 \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function N_direction \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:5 --data_device cuda:5 