"""Job Dashboard menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import slurm


def job_dashboard_menu(ssh_conn):
    """Job Dashboard submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        choice = questionary.select(
            "📊 Job Dashboard:",
            choices=[
                "🏃 Running Jobs",
                "⏳ Pending Jobs",
                questionary.Separator("─── Job Details ───"),
                "📋 Job Details by ID",
                questionary.Separator("─── Actions ───"),
                "🛑 Cancel Job",
                "? Node Information",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "🏃 Running Jobs":
            slurm.job_get_running(ssh_conn)
        elif choice == "⏳ Pending Jobs":
            slurm.job_get_pending(ssh_conn)
        elif choice == "📋 Job Details by ID":
            job_id = questionary.text("Enter Job ID:", style=custom_style).ask()
            if job_id:
                slurm.slurm_job_info(ssh_conn, job_id)
        elif choice == "🛑 Cancel Job":
            job_id = questionary.text("Enter Job ID to cancel:", style=custom_style).ask()
            if job_id:
                if questionary.confirm(f"Cancel job {job_id}?", default=False, style=custom_style).ask():
                    slurm.slurm_cancel_job(ssh_conn, job_id)
        elif choice == "? Node Information":
            slurm.slurm_nodes_info(ssh_conn)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
