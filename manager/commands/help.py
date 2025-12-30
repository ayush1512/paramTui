"""Help and documentation commands."""

from rich.console import Console
from rich.panel import Panel

console = Console()


def help_slurm_cheatsheet():
    """Display SLURM cheat sheet."""
    cheatsheet = """
[bold cyan]📋 SLURM Cheat Sheet[/bold cyan]

[bold green]Job Submission:[/bold green]
  sbatch script.sh       Submit a batch job
  srun command           Run a command on allocated resources
  salloc                 Allocate resources for interactive use

[bold green]Job Monitoring:[/bold green]
  squeue -u $USER        Show your jobs
  squeue -j <jobid>      Show specific job
  scancel <jobid>        Cancel a job
  scontrol show job      Detailed job info

[bold green]Job History:[/bold green]
  sacct -u $USER         Job accounting info
  seff <jobid>           Job efficiency report

[bold green]Resource Info:[/bold green]
  sinfo                  Show partition info
  sinfo -N -l            Detailed node info
  scontrol show node     Node details

[bold green]Common Options:[/bold green]
  --nodes=N              Number of nodes
  --ntasks=N             Number of tasks
  --cpus-per-task=N      CPUs per task
  --mem=XG               Memory per node
  --time=HH:MM:SS        Time limit
  --gres=gpu:N           GPU resources
  --partition=name       Partition/queue
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
  • Software module management
  • Resource monitoring
  • Job templates for quick submission
  • Interactive Jupyter sessions

[bold yellow]Version:[/bold yellow] 1.0.0
[bold yellow]Author:[/bold yellow] PARAM Team
"""
    console.print(Panel(about_text, title="📖 About", border_style="cyan"))
