"""Job Templates menu."""

import questionary
from rich.panel import Panel
from manager.ui.styles import custom_style, print_header, console
from manager.commands import job_templates


def job_templates_menu(ssh_conn):
    """Job Templates submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "🧾 Job Templates:",
            choices=[
                "📋 List Available Templates",
                questionary.Separator("─── Quick Submit ───"),
                "🐍 Python Job",
                "🔄 MPI Job",
                "🎮 CUDA/GPU Job",
                "🔥 PyTorch Job",
                "📊 TensorFlow Job",
                questionary.Separator("─── Custom ───"),
                "✏️  Create Custom Job Script",
                "📁 Submit Existing Script",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "📋 List Available Templates":
            job_templates.template_list()
        elif choice == "🐍 Python Job":
            job_name = questionary.text("Job name:", default="python_job", style=custom_style).ask()
            script_path = questionary.text("Python script path:", style=custom_style).ask()
            conda_env = questionary.text("Conda environment:", default="base", style=custom_style).ask()
            
            if job_name and script_path:
                script = job_templates.template_generate("python", job_name=job_name, script_path=script_path, conda_env=conda_env)
                if script:
                    console.print(Panel(script, title="Generated Script", border_style="green"))
                    if questionary.confirm("Submit this job?", style=custom_style).ask():
                        script_file = f"~/{job_name}.sh"
                        job_templates.template_save(ssh_conn, script, script_file)
                        job_templates.template_submit(ssh_conn, script_file)
        elif choice == "🔄 MPI Job":
            job_name = questionary.text("Job name:", default="mpi_job", style=custom_style).ask()
            executable = questionary.text("Executable path:", style=custom_style).ask()
            nodes = questionary.text("Number of nodes:", default="2", style=custom_style).ask()
            tasks_per_node = questionary.text("Tasks per node:", default="4", style=custom_style).ask()
            
            if job_name and executable:
                script = job_templates.template_generate("mpi", job_name=job_name, executable=executable, 
                                                          nodes=nodes, tasks_per_node=tasks_per_node)
                if script:
                    console.print(Panel(script, title="Generated Script", border_style="green"))
                    if questionary.confirm("Submit this job?", style=custom_style).ask():
                        script_file = f"~/{job_name}.sh"
                        job_templates.template_save(ssh_conn, script, script_file)
                        job_templates.template_submit(ssh_conn, script_file)
        elif choice == "🎮 CUDA/GPU Job":
            job_name = questionary.text("Job name:", default="cuda_job", style=custom_style).ask()
            command = questionary.text("Command to run:", style=custom_style).ask()
            num_gpus = questionary.text("Number of GPUs:", default="1", style=custom_style).ask()
            
            if job_name and command:
                script = job_templates.template_generate("cuda", job_name=job_name, command=command, num_gpus=num_gpus)
                if script:
                    console.print(Panel(script, title="Generated Script", border_style="green"))
                    if questionary.confirm("Submit this job?", style=custom_style).ask():
                        script_file = f"~/{job_name}.sh"
                        job_templates.template_save(ssh_conn, script, script_file)
                        job_templates.template_submit(ssh_conn, script_file)
        elif choice == "🔥 PyTorch Job":
            job_name = questionary.text("Job name:", default="pytorch_job", style=custom_style).ask()
            script_path = questionary.text("Python script path:", style=custom_style).ask()
            conda_env = questionary.text("Conda environment:", default="pytorch", style=custom_style).ask()
            num_gpus = questionary.text("Number of GPUs:", default="1", style=custom_style).ask()
            
            if job_name and script_path:
                script = job_templates.template_generate("pytorch", job_name=job_name, script_path=script_path,
                                                          conda_env=conda_env, num_gpus=num_gpus)
                if script:
                    console.print(Panel(script, title="Generated Script", border_style="green"))
                    if questionary.confirm("Submit this job?", style=custom_style).ask():
                        script_file = f"~/{job_name}.sh"
                        job_templates.template_save(ssh_conn, script, script_file)
                        job_templates.template_submit(ssh_conn, script_file)
        elif choice == "📊 TensorFlow Job":
            job_name = questionary.text("Job name:", default="tensorflow_job", style=custom_style).ask()
            script_path = questionary.text("Python script path:", style=custom_style).ask()
            conda_env = questionary.text("Conda environment:", default="tensorflow", style=custom_style).ask()
            num_gpus = questionary.text("Number of GPUs:", default="1", style=custom_style).ask()
            
            if job_name and script_path:
                script = job_templates.template_generate("tensorflow", job_name=job_name, script_path=script_path,
                                                          conda_env=conda_env, num_gpus=num_gpus)
                if script:
                    console.print(Panel(script, title="Generated Script", border_style="green"))
                    if questionary.confirm("Submit this job?", style=custom_style).ask():
                        script_file = f"~/{job_name}.sh"
                        job_templates.template_save(ssh_conn, script, script_file)
                        job_templates.template_submit(ssh_conn, script_file)
        elif choice == "✏️  Create Custom Job Script":
            console.print("[bold cyan]Opening interactive shell for script creation...[/bold cyan]")
            console.print("[dim]Create your script using vim/nano and save it.[/dim]")
            ssh_conn.interactive_shell()
        elif choice == "📁 Submit Existing Script":
            script_path = questionary.text("Path to SLURM script:", style=custom_style).ask()
            if script_path:
                job_templates.template_submit(ssh_conn, script_path)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
