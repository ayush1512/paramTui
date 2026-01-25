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
                # "✅ Completed Jobs (Last 7 days)",
                # "❌ Failed Jobs (Last 7 days)",
                questionary.Separator("─── Job Details ───"),
                "📋 Job Details by ID",
                # "📈 Job Resource Usage",
                "📄 View Job Log (.out)",
                "📄 View Job Log (.err)",
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
        # elif choice == "✅ Completed Jobs (Last 7 days)":
        #     slurm.job_get_completed(ssh_conn, 7)
        # elif choice == "❌ Failed Jobs (Last 7 days)":
        #     slurm.job_get_failed(ssh_conn, 7)
        elif choice == "📋 Job Details by ID":
            job_id = questionary.text("Enter Job ID:", style=custom_style).ask()
            if job_id:
                slurm.slurm_job_info(ssh_conn, job_id)
        # elif choice == "📈 Job Resource Usage":
        #     job_id = questionary.text("Enter Job ID:", style=custom_style).ask()
        #     if job_id:
        #         slurm.job_resource_usage(ssh_conn, job_id)
        # elif choice == "📄 View Job Log (.out)":
        #     job_id = questionary.text("Enter Job ID:", style=custom_style).ask()
        #     if job_id:
        #         slurm.job_view_log(ssh_conn, job_id, "out")
        # elif choice == "📄 View Job Log (.err)":
        #     job_id = questionary.text("Enter Job ID:", style=custom_style).ask()
        #     if job_id:
        #         slurm.job_view_log(ssh_conn, job_id, "err")
        elif choice == "🛑 Cancel Job":
            job_id = questionary.text("Enter Job ID to cancel:", style=custom_style).ask()
            if job_id:
                if questionary.confirm(f"Cancel job {job_id}?", default=False, style=custom_style).ask():
                    slurm.slurm_cancel_job(ssh_conn, job_id)
        elif choice == "🖧 Node Information":
            slurm.slurm_nodes_info(ssh_conn)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
