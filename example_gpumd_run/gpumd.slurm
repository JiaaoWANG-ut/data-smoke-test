#!/bin/bash -l

#SBATCH --job-name=jiaao
#SBATCH --output=ll_out
#SBATCH --gres=gpu:a100:1

/home/jiaao/GPUMD/src/gpumd
