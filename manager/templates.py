"""Job templates for SLURM submissions."""

JOB_TEMPLATES = {
    "python": """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err

module load python/3.9
source activate {conda_env}

python {script_path}
""",
    "mpi": """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes={nodes}
#SBATCH --ntasks-per-node={tasks_per_node}
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err

module load openmpi/4.1.1

mpirun -np $SLURM_NTASKS {executable}
""",
    "cuda": """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:{num_gpus}
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --partition=gpu
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err

module load cuda/11.8

{command}
""",
    "pytorch": """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:{num_gpus}
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --partition=gpu
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err

module load cuda/11.8
module load python/3.9
source activate {conda_env}

python {script_path}
""",
    "tensorflow": """#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:{num_gpus}
#SBATCH --mem=64G
#SBATCH --time=24:00:00
#SBATCH --partition=gpu
#SBATCH --output={job_name}_%j.out
#SBATCH --error={job_name}_%j.err

module load cuda/11.8
module load cudnn/8.6
module load python/3.9
source activate {conda_env}

python {script_path}
""",
    "jupyter": """#!/bin/bash
#SBATCH --job-name=jupyter_{job_name}
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:{num_gpus}
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --partition=gpu
#SBATCH --output=jupyter_%j.out
#SBATCH --error=jupyter_%j.err

module load python/3.9
source activate {conda_env}

# Get the node hostname
NODE=$(hostname)
PORT={port}

echo "=========================================="
echo "Jupyter is running on: $NODE:$PORT"
echo "SSH tunnel command:"
echo "ssh -L $PORT:$NODE:$PORT {user}@{host} -p {ssh_port}"
echo "=========================================="

jupyter {jupyter_type} --no-browser --port=$PORT --ip=0.0.0.0
"""
}
