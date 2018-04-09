#!/bin/bash

username=larryzhang
remote_machine=aniseed

placenta_dir=/data/vision/polina/projects/placenta_segmentation/

###################

remote_ssh=${username}@${remote_machine}.csail.mit.edu

run_cmd="scp -r ${remote_ssh}:${placenta_dir}/data/predict/* ./data/predict/"

eval ${run_cmd}