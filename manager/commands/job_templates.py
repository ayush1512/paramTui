"""Job template management commands."""

import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from manager.templates import JOB_TEMPLATES

console = Console()


def template_list():
    """List available job templates."""
    table = Table(title="📝 Available Job Templates", box=box.ROUNDED)
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="green")
    
    templates_info = {
        "python": "Basic Python script execution",
        "mpi": "MPI parallel job",
        "cuda": "CUDA GPU job",
        "pytorch": "PyTorch deep learning job",
        "tensorflow": "TensorFlow deep learning job",
        "jupyter": "Jupyter Notebook/Lab session",
    }
    
    for name, desc in templates_info.items():
        table.add_row(name, desc)
    
    console.print(table)
    return list(templates_info.keys())


def template_generate(template_name, **kwargs):
    """Generate a job script from template."""
    if template_name not in JOB_TEMPLATES:
        console.print(f"[bold red]Template '{template_name}' not found![/bold red]")
        return None
    
    try:
        script = JOB_TEMPLATES[template_name].format(**kwargs)
        return script
    except KeyError as e:
        console.print(f"[bold red]Missing parameter: {e}[/bold red]")
        return None


def template_save(ssh_conn, script_content, filename):
    """Save a job script to remote server."""
    cmd = f"cat > {filename} << 'SCRIPT_EOF'\n{script_content}\nSCRIPT_EOF"
    ssh_conn.execute_command(cmd)
    console.print(f"[bold green]✓ Script saved to: {filename}[/bold green]")
    return filename


def template_submit(ssh_conn, script_path):
    """Submit a job script."""
    output = ssh_conn.execute_command(f"sbatch {script_path}")
    if output:
        console.print(f"[bold green]✓ Job submitted![/bold green]")
        console.print(output)
        return True
    return False


def interactive_start_jupyter(ssh_conn, jupyter_type="notebook", conda_env="base", num_gpus=0, port=8888):
    """Start Jupyter Notebook/Lab via SLURM."""
    template = JOB_TEMPLATES["jupyter"]
    script = template.format(
        job_name="jupyter",
        conda_env=conda_env,
        num_gpus=num_gpus,
        port=port,
        jupyter_type=jupyter_type,
        user=ssh_conn.user,
        host=ssh_conn.host,
        ssh_port=ssh_conn.port
    )
    
    script_path = f"~/.jupyter_job_{port}.sh"
    ssh_conn.execute_command(f"cat > {script_path} << 'EOF'\n{script}\nEOF")
    
    output = ssh_conn.execute_command(f"sbatch {script_path}")
    if output:
        console.print(f"[bold green]✓ Jupyter {jupyter_type} job submitted![/bold green]")
        console.print(output)
        console.print(f"\n[bold cyan]Once the job starts, create an SSH tunnel:[/bold cyan]")
        console.print(f"[yellow]ssh -L {port}:<node>:{port} {ssh_conn.user}@{ssh_conn.host} -p {ssh_conn.port}[/yellow]")
        console.print(f"\n[bold cyan]Then open in browser:[/bold cyan] http://localhost:{port}")
        return True
    return False


def interactive_gpu_session(ssh_conn, num_gpus=1, time="02:00:00", mem="16G"):
    """Start an interactive GPU session."""
    console.print(f"[bold yellow]Starting interactive GPU session ({num_gpus} GPU(s))...[/bold yellow]")
    console.print("[dim]This will open an interactive shell. Type 'exit' to end the session.[/dim]\n")
    
    cmd = f"srun --gres=gpu:{num_gpus} --time={time} --mem={mem} --pty bash"
    try:
        subprocess.run(
            f"ssh -S {ssh_conn.control_path} -t -p {ssh_conn.port} {ssh_conn.user}@{ssh_conn.host} '{cmd}'",
            shell=True
        )
    except Exception as e:
        console.print(f"[bold red]Session error: {str(e)}[/bold red]")

def interactive_cpu_session(ssh_conn, num_cpus=1, time="02:00:00", core="40"):
    """Start an interactive GPU session."""
    console.print(f"[bold yellow]Starting interactive CPU session ({num_cpus} CPU(s))...[/bold yellow]")
    console.print("[dim]This will open an interactive shell. Type 'exit' to end the session.[/dim]\n")
    
    cmd = f"srun --partition=cpu -N {num_cpus} --time={time} -c {core} --pty bash"
    try:
        subprocess.run(
            f"ssh -S {ssh_conn.control_path} -t -p {ssh_conn.port} {ssh_conn.user}@{ssh_conn.host} '{cmd}'",
            shell=True
        )
    except Exception as e:
        console.print(f"[bold red]Session error: {str(e)}[/bold red]")

def interactive_list_notebooks(ssh_conn):
    """List running Jupyter jobs."""
    output = ssh_conn.execute_command("squeue -u $USER -n jupyter_* -o '%.18i %.15j %.8T %.10M %.R' 2>/dev/null")
    if output and len(output.strip().split('\n')) > 1:
        console.print("[bold green]📓 Running Jupyter Sessions:[/bold green]")
        console.print(output)
        return True
    console.print("[yellow]No active Jupyter sessions found.[/yellow]")
    return False
