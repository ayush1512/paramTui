"""Software module management commands."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()


def module_list_available(ssh_conn, pattern=None):
    """List available modules."""
    cmd = f"module avail {pattern} 2>&1" if pattern else "module avail 2>&1"
    output = ssh_conn.execute_command(cmd)
    if output:
        console.print(Panel(output, title="📦 Available Modules", border_style="cyan"))
        return True
    return False


def module_list_loaded(ssh_conn):
    """List currently loaded modules."""
    output = ssh_conn.execute_command("module list 2>&1")
    if output:
        console.print(Panel(output, title="✅ Loaded Modules", border_style="green"))
        return True
    return False


def module_load(ssh_conn, module_name):
    """Load a module."""
    output = ssh_conn.execute_command(f"module load {module_name} 2>&1 && echo 'MODULE_LOADED'")
    if output and 'MODULE_LOADED' in output:
        console.print(f"[bold green]✓ Module loaded: {module_name}[/bold green]")
        return True
    console.print(f"[bold red]✗ Failed to load module: {module_name}[/bold red]")
    if output:
        console.print(f"[dim]{output}[/dim]")
    return False


def module_unload(ssh_conn, module_name):
    """Unload a module."""
    output = ssh_conn.execute_command(f"module unload {module_name} 2>&1 && echo 'MODULE_UNLOADED'")
    if output and 'MODULE_UNLOADED' in output:
        console.print(f"[bold green]✓ Module unloaded: {module_name}[/bold green]")
        return True
    console.print(f"[bold red]✗ Failed to unload module[/bold red]")
    return False


def module_search(ssh_conn, keyword):
    """Search for modules by keyword."""
    output = ssh_conn.execute_command(f"module avail 2>&1 | grep -i {keyword}")
    if output:
        console.print(f"[bold green]🔍 Modules matching '{keyword}':[/bold green]")
        console.print(output)
        return True
    console.print(f"[yellow]No modules found matching '{keyword}'[/yellow]")
    return False


def module_get_recommended_sets():
    """Get recommended module sets for different use cases."""
    sets = {
        "🧠 AI/Deep Learning": ["python/3.9", "cuda/11.8", "cudnn/8.6", "pytorch/2.0", "tensorflow/2.12"],
        "🔬 Computational Fluid Dynamics": ["openmpi/4.1", "hdf5/1.12", "openfoam/2212"],
        "🧬 Bioinformatics": ["python/3.9", "blast/2.13", "samtools/1.16", "bwa/0.7.17"],
        "⚡ High Performance Computing": ["openmpi/4.1", "fftw/3.3", "hdf5/1.12", "petsc/3.18"],
        "📊 Data Science": ["python/3.9", "r/4.2", "julia/1.9", "jupyter"],
    }
    
    table = Table(title="🧩 Recommended Module Sets", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Modules", style="green")
    
    for category, modules in sets.items():
        table.add_row(category, ", ".join(modules))
    
    console.print(table)
    return sets
