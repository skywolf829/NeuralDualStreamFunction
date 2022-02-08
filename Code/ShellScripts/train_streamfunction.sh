#!/bin/sh
cd /lus/theta-fs0/projects/DL4VIS/ImplicitStreamFunction

python3 -u Code/train.py --n_outputs 1 --n_dims 3 \
--signal_file_name synthetic_VF1.h5 \
--save_name synth1 \
--n_layers 4 --nodes_per_layer 128 \
--points_per_iteration 100000 \
--iterations 10000 \
--fit_gradient true \
--loss magangle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:0 --data_device cuda:0 &

python3 -u Code/train.py --n_outputs 3 --n_dims 3 \
--signal_file_name synthetic_VF3.h5 \
--save_name synth3_streamfunction \
--n_layers 4 --nodes_per_layer 128 \
--points_per_iteration 100000 \
--iterations 10000 \
--streamfunction true \
--loss magangle_same --lr 5e-5 \
--log_image false --log_gradient false \
--device cuda:1 --data_device cuda:1