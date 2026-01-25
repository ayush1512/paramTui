"""Help and documentation commands."""

from rich.console import Console
from rich.panel import Panel

console = Console()

def help_slurm_cheatsheet():
    """Display SLURM cheat sheet."""
    cheatsheet = """
  [bold cyan]📋 SLURM Cheat Sheet[/bold cyan]

  [bold green]Quick sbatch script example:[/bold green]
    #!/bin/bash
    #SBATCH --job-name=training
    #SBATCH --output=out.%j.log
    #SBATCH --error=err.%j.log
    #SBATCH --nodes=1
    #SBATCH --ntasks=1
    #SBATCH --cpus-per-task=8
    #SBATCH --gres=gpu:1
    #SBATCH --mem=32G
    #SBATCH --time=02:00:00
    #SBATCH --partition=gpu
    module purge
    module load anaconda/3
    source activate myenv
    srun python train.py --epochs 10

  [bold green]Common sbatch flags (CLI):[/bold green]
    sbatch --job-name=name --output=out.%j.log --partition=gpu --gres=gpu:1 script.sh
    sbatch --array=1-10%3 array_script.sh      Run job arrays (limit concurrent with %)
    sbatch --dependency=afterok:<jobid> script.sh   Chain jobs on success
    sbatch --wrap="python -u quick_task.py"     Submit single command

  [bold green]srun examples:[/bold green]
    srun --pty --nodes=1 --ntasks=1 --cpus-per-task=4 bash    Interactive shell in allocation
    srun -n 16 --mpi=pmi2 ./mpi_program                      Run MPI across 16 tasks
    srun --gres=gpu:2 python train.py                        Launch task within job

  [bold green]salloc (interactive allocation):[/bold green]
    salloc --nodes=1 --gres=gpu:1 --time=01:00:00
    # then inside allocation:
    srun --pty bash
    # or run Jupyter:
    srun --mem=16G --cpus-per-task=4 jupyter lab --no-browser --port=8888

  [bold green]Monitoring & info:[/bold green]
    squeue -u $USER                        Show current jobs
    squeue -j <jobid>                      Show specific job
    squeue -o "%.18i %.9P %.8j %.8u %.2t %.10M %.6D %R"  Custom output format
    sacct -j <jobid> --format=JobID,JobName,State,ExitCode,Elapsed         Accounting
    seff <jobid>                           Efficiency (CPU/GPU/memory usage)
    sinfo -s                                Summary of partitions
    sinfo -N -l                             Detailed node listing
    scontrol show job <jobid>               Full job details
    scontrol show node <nodename>           Node diagnostics

  [bold green]Job control:[/bold green]
    scancel <jobid>                         Cancel job
    scancel -u $USER                        Cancel all your jobs
    scontrol update JobId=<jobid> TimeLimit=HH:MM:SS  Modify job (if permitted)

  [bold green]Resource & environment tips:[/bold green]
    --gres=gpu:V100:1 or --gres=gpu:1        Request specific GPU type if supported
    --mem=32G                                Memory per node; use --mem-per-cpu for per-core
    --cpus-per-task=8                        Useful for multithreaded tasks
    export OMP_NUM_THREADS=8                 Match threads to cpus-per-task
    echo $SLURM_JOB_ID                       Job ID accessible in scripts
    echo $SLURM_NTASKS $SLURM_NNODES         Common SLURM env vars

  [bold green]Job arrays & parametrization:[/bold green]
    #SBATCH --array=0-9
    TASK_ID=${SLURM_ARRAY_TASK_ID}
    INPUT=file_${TASK_ID}.txt
    # run array with per-task inputs or offsets

  [bold green]Checkpointing & restarts (pattern):[/bold green]
    # write periodic checkpoints to $SCRATCH or $TMPDIR
    # save model state with step number or epoch
    # on restart, read latest checkpoint and submit continuation via --dependency

  [bold green]Interactive GPU debugging:[/bold green]
    srun --pty --gres=gpu:1 --mem=16G --cpus-per-task=4 --time=00:30:00 bash
    # run nvidia-smi to inspect GPU allocation and processes

  [bold green]Data transfer & staging tips:[/bold green]
    rsync -avP local_dir user@host:/scratch/$USER/project/   Efficient sync of datasets
    scp file user@host:/scratch/$USER/                       Simple copy for small files
    Use $SCRATCH or $TMPDIR on compute nodes for I/O-heavy operations, then rsync back

  [bold green]Troubleshooting commands:[/bold green]
    scontrol show job <jobid>         Inspect job reasons for PENDING
    scontrol show partition <part>    See partition limits and nodes
    journalctl -u slurmctld          (admin-only) cluster controller logs
    module avail | grep -i <name>     Find available modules

  [bold green]Useful patterns:[/bold green]
    # Submit and track:
    jid=$(sbatch --parsable train.sh)
    squeue -j $jid
    # Submit dependent job:
    sbatch --dependency=afterok:$jid evaluate.sh

  [bold green]Shortcuts & sensible defaults:[/bold green]
    --time=01:00:00  small debug
    --time=24:00:00  typical training epoch
    --partition=debug  short-queue for quick tests (if available)

  [bold yellow]Remember:[/bold yellow] Check your cluster's documentation for partition names, available GPUs, and site-specific sbatch directives.
  """
    console.print(Panel(cheatsheet, title="📚 SLURM Quick Reference", border_style="cyan"))


def help_common_errors():
    """Display common errors and fixes."""
    errors = """
[bold cyan]🔧 Common Errors & Fixes[/bold cyan]

[bold red]Job stuck in PENDING with (Priority):[/bold red]
  → Wait for higher priority jobs to complete
  → Check partition limits: scontrol show partition

[bold red]Job stuck in PENDING with (Resources):[/bold red]
  → Requested resources unavailable
  → Try: reduce nodes/memory/time or different partition

[bold red]CUDA out of memory:[/bold red]
  → Reduce batch size
  → Use gradient accumulation
  → Request more GPU memory

[bold red]Module not found:[/bold red]
  → Run: module avail | grep -i <name>
  → Check for typos in module name

[bold red]Permission denied:[/bold red]
  → Check file permissions: ls -la
  → Use chmod to fix: chmod +x script.sh

[bold red]Connection timeout:[/bold red]
  → Check network connectivity
  → Verify SSH port and hostname
  → Try reconnecting
"""
    console.print(Panel(errors, title="🔧 Troubleshooting Guide", border_style="yellow"))


def help_about():
    """Display about information."""
    about_text = """
[bold cyan]PARAM SSH Manager & HPC Console[/bold cyan]

A modern terminal user interface for managing HPC clusters.

[bold green]Features:[/bold green]
  • SSH connection management with ControlMaster
  • SLURM job submission and monitoring
  • File management (upload/download/browse)
  • Conda environment management

[bold yellow]Version:[/bold yellow] 1.0.0
[bold yellow]Author:[/bold yellow] [link=https://github.com/ayush1512]Ayush Saxena[/link]
"""
    console.print(Panel(about_text, title="📖 About", border_style="cyan"))
