import questionary
from manager import system
from rich.console import Console

console = Console()

def connection_menu():
    """Initial menu to establish SSH connection."""
    console.clear()
    console.print("[bold blue]========== PARAM - SSH Manager ==========[/bold blue]", justify="center")
    console.print()
    
    host = questionary.text("Enter Host PARAM IP or Domain:", default="paramutkarsh.cdac.in").ask()
    if not host:
        return None
    
    user = questionary.text("Enter Username:", default="").ask()
    if not user:
        return None
    
    port = questionary.text("Enter Port:", default="4422").ask()
    if not port:
        return None
    
    # console.print("\n[bold cyan]Multi-step Authentication Required:[/bold cyan]")
    # console.print("  [dim]1. Answer the question[/dim]")
    # console.print("  [dim]2. Enter OTP[/dim]")
    # console.print("  [dim]3. Enter password[/dim]\n")
    
    ssh_conn = system.SSHConnection()
    success = ssh_conn.connect(host, user, port)
    
    if success:
        return ssh_conn
    else:
        console.print("[bold red]Failed to connect. Exiting...[/bold red]")
        return None


def slurm_menu(ssh_conn):
    """SLURM management submenu."""
    while True:
        choice = questionary.select(
            "SLURM Manager:",
            choices=[
                "Show My Jobs",
                "Submit Job",
                "Cancel Job",
                "Job Details",
                "Nodes Info",
                questionary.Separator(),
                "← Back to Main Menu"
            ]
        ).ask()
        
        if choice == "Show My Jobs":
            system.slurm_show_jobs(ssh_conn)
        elif choice == "Submit Job":
            script_path = questionary.text("Enter path to SLURM script:").ask()
            if script_path:
                system.slurm_submit_job(ssh_conn, script_path)
        elif choice == "Cancel Job":
            job_id = questionary.text("Enter Job ID to cancel:").ask()
            if job_id:
                system.slurm_cancel_job(ssh_conn, job_id)
        elif choice == "Job Details":
            job_id = questionary.text("Enter Job ID:").ask()
            if job_id:
                system.slurm_job_info(ssh_conn, job_id)
        elif choice == "Nodes Info":
            system.slurm_nodes_info(ssh_conn)
        elif choice == "← Back to Main Menu":
            break
        
        questionary.press_any_key_to_continue().ask()
        console.clear()


def conda_menu(ssh_conn):
    """Conda package manager submenu."""
    while True:
        choice = questionary.select(
            "Conda Package Manager:",
            choices=[
                "List Environments",
                "Activate Environment",
                "Create Environment",
                "Remove Environment",
                "Install Package",
                questionary.Separator(),
                "← Back to Main Menu"
            ]
        ).ask()
        
        if choice == "List Environments":
            system.conda_list_envs(ssh_conn)
        elif choice == "Activate Environment":
            env_name = questionary.text("Enter environment name:").ask()
            if env_name:
                system.conda_activate_env(ssh_conn,env_name)
        elif choice == "Create Environment":
            env_name = questionary.text("Enter environment name:").ask()
            python_ver = questionary.text("Python version (leave empty for default):", default="").ask()
            if env_name:
                system.conda_create_env(ssh_conn, env_name, python_ver if python_ver else None)
        elif choice == "Remove Environment":
            env_name = questionary.text("Enter environment name to remove:").ask()
            if env_name:
                confirm = questionary.confirm(f"Are you sure you want to remove '{env_name}'?").ask()
                if confirm:
                    system.conda_remove_env(ssh_conn, env_name)
        elif choice == "Install Package":
            env_name = questionary.text("Enter environment name:").ask()
            package = questionary.text("Enter package name:").ask()
            if env_name and package:
                system.conda_install_package(ssh_conn, env_name, package)
        elif choice == "← Back to Main Menu":
            break
        
        questionary.press_any_key_to_continue().ask()
        console.clear()


def main_menu():
    """Main menu after SSH connection is established."""
    # Step 1: Establish SSH Connection
    ssh_conn = connection_menu()
    
    if not ssh_conn:
        return
    
    # Step 2: Show management options
    console.clear()
    console.print(f"[bold green]✓ Connected to {ssh_conn.user}@{ssh_conn.host}[/bold green]", justify="center")
    console.print()
    
    while True:
        choice = questionary.select(
            "What would you like to manage?",
            choices=[
                "SLURM Manager",
                "Conda Package Manager",
                "Launch SSH Tunnel",
                "Interactive Shell",
                "Remote System Info",
                questionary.Separator(),
                "Disconnect & Exit"
            ]
        ).ask()
        
        if choice == "SLURM Manager":
            slurm_menu(ssh_conn)
        elif choice == "Conda Package Manager":
            conda_menu(ssh_conn)
        elif choice == "Launch SSH Tunnel":
            remote_port = questionary.text("Enter remote port:", default="8888").ask()
            local_port = questionary.text("Enter local port (leave empty to use same):", default="").ask()
            if remote_port:
                system.create_tunnel(
                    ssh_conn,  # Pass the connection object
                    remote_port, 
                    local_port if local_port else None
                )
        elif choice == "Interactive Shell":
            ssh_conn.interactive_shell()
        elif choice == "Remote System Info":
            system.get_remote_system_info(ssh_conn)
        elif choice == "Disconnect & Exit":
            ssh_conn.disconnect()
            console.print("[bold yellow]Goodbye![/bold yellow]")
            break
        
        questionary.press_any_key_to_continue().ask()
        console.clear()
        console.print(f"[bold green]✓ Connected to {ssh_conn.user}@{ssh_conn.host}[/bold green]", justify="center")
        console.print()