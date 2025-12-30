"""Interactive Tools menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import job_templates


def interactive_tools_menu(ssh_conn):
    """Interactive Tools submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "🧠 Interactive Tools:",
            choices=[
                "📓 Start Jupyter Notebook",
                "🔬 Start JupyterLab",
                "🎮 GPU Interactive Session",
                "📋 List Active Notebooks",
                "🖥️  Interactive Shell",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice in ["📓 Start Jupyter Notebook", "🔬 Start JupyterLab"]:
            jupyter_type = "notebook" if "Notebook" in choice else "lab"
            
            conda_env = questionary.text("Conda environment:", default="base", style=custom_style).ask()
            num_gpus = questionary.text("Number of GPUs (0 for CPU only):", default="0", style=custom_style).ask()
            port = questionary.text("Port:", default="8888", style=custom_style).ask()
            
            if conda_env and port:
                job_templates.interactive_start_jupyter(
                    ssh_conn, 
                    jupyter_type=jupyter_type,
                    conda_env=conda_env,
                    num_gpus=int(num_gpus) if num_gpus else 0,
                    port=int(port) if port else 8888
                )
        elif choice == "🎮 GPU Interactive Session":
            num_gpus = questionary.text("Number of GPUs:", default="1", style=custom_style).ask()
            time_limit = questionary.text("Time limit (HH:MM:SS):", default="02:00:00", style=custom_style).ask()
            memory = questionary.text("Memory:", default="16G", style=custom_style).ask()
            
            if num_gpus and time_limit:
                job_templates.interactive_gpu_session(
                    ssh_conn,
                    num_gpus=int(num_gpus),
                    time=time_limit,
                    mem=memory
                )
        elif choice == "📋 List Active Notebooks":
            job_templates.interactive_list_notebooks(ssh_conn)
        elif choice == "🖥️  Interactive Shell":
            ssh_conn.interactive_shell()
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
