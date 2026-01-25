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
                "🎮 GPU Interactive Session",
                "🖥️  CPU Interactive Session",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "🎮 GPU Interactive Session":
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
        elif choice == "🖥️  CPU Interactive Session":
            num_cpus = questionary.text("Number of CPUs:", default="1", style=custom_style).ask()
            time_limit = questionary.text("Time limit (HH:MM:SS):", default="02:00:00", style=custom_style).ask()
            cores = questionary.text("Number of cpus required per task:", default="40", style=custom_style).ask()
            if num_cpus and time_limit:
                job_templates.interactive_cpu_session(
                    ssh_conn,
                    num_cpus=int(num_cpus),
                    time=time_limit,
                    core=cores,
                )
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
