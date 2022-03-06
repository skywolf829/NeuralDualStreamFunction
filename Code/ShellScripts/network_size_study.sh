#!/bin/sh
cd /lus/theta-fs0/projects/DL4VIS/NeuralDualStreamFunction

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name network_size_study_isabel_sm_residual \
--n_layers 2 --nodes_per_layer 128 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:0 --data_device cuda:0 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name network_size_study_tornado_sm_residual \
--n_layers 2 --nodes_per_layer 128 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:1 --data_device cuda:1 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name network_size_study_isabel_md_residual \
--n_layers 3 --nodes_per_layer 256 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:2 --data_device cuda:2 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name network_size_study_tornado_md_residual \
--n_layers 3 --nodes_per_layer 256 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:3 --data_device cuda:3 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name network_size_study_isabel_lg_residual \
--n_layers 3 --nodes_per_layer 512 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:4 --data_device cuda:4 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name network_size_study_tornado_lg_residual \
--n_layers 3 --nodes_per_layer 512 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:5 --data_device cuda:5 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name network_size_study_isabel_xl_residual \
--n_layers 4 --nodes_per_layer 512 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:6 --data_device cuda:6 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name network_size_study_tornado_xl_residual \
--n_layers 4 --nodes_per_layer 512 \
--points_per_iteration 100000 \
--residual true \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:7 --data_device cuda:7 

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name network_size_study_isabel_sm \
--n_layers 4 --nodes_per_layer 128 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:0 --data_device cuda:0 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name network_size_study_tornado_sm \
--n_layers 4 --nodes_per_layer 128 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:1 --data_device cuda:1 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name network_size_study_isabel_md \
--n_layers 6 --nodes_per_layer 256 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:2 --data_device cuda:2 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name network_size_study_tornado_md \
--n_layers 6 --nodes_per_layer 256 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:3 --data_device cuda:3 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name network_size_study_isabel_lg \
--n_layers 6 --nodes_per_layer 512 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:4 --data_device cuda:4 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name network_size_study_tornado_lg \
--n_layers 6 --nodes_per_layer 512 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:5 --data_device cuda:5 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name isabel.h5 \
--save_name network_size_study_isabel_xl \
--n_layers 8 --nodes_per_layer 512 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:6 --data_device cuda:6 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name tornado3d.h5 \
--save_name network_size_study_tornado_xl \
--n_layers 8 --nodes_per_layer 512 \
--points_per_iteration 100000 \
--residual false \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:7 --data_device cuda:7 

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name network_size_study_plume_sm_residual \
--n_layers 2 --nodes_per_layer 128 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:0 --data_device cuda:0 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name network_size_study_plume_md_residual \
--n_layers 3 --nodes_per_layer 256 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:1 --data_device cuda:1 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name network_size_study_plume_lg_residual \
--n_layers 3 --nodes_per_layer 512 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:2 --data_device cuda:2 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name network_size_study_plume_xl_residual \
--n_layers 4 --nodes_per_layer 512 \
--residual true \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:3 --data_device cuda:3 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name network_size_study_plume_sm \
--n_layers 4 --nodes_per_layer 128 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:4 --data_device cuda:4 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name network_size_study_plume_md \
--n_layers 6 --nodes_per_layer 256 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:5 --data_device cuda:5 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name network_size_study_plume_lg \
--n_layers 6 --nodes_per_layer 512 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:6 --data_device cuda:6 &

python -u Code/train.py --n_outputs 2 --n_dims 3 \
--signal_file_name plume.h5 \
--save_name network_size_study_plume_xl \
--n_layers 8 --nodes_per_layer 512 \
--residual false \
--points_per_iteration 100000 \
--iterations 10000 \
--dual_stream_function any \
--loss angle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:7 --data_device cuda:7 