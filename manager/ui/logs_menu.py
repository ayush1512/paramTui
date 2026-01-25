"""Logs menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import logs, files


def logs_menu(ssh_conn):
    """Logs submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "🧪 Logs:",
            choices=[
                "📋 SSH Session History",
                "📝 Job Submission History",
                "❌ Find Error Logs",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "📋 SSH Session History":
            logs.logs_get_session_history(ssh_conn)
        elif choice == "📝 Job Submission History":
            days = questionary.text("Days to look back:", default="7", style=custom_style).ask()
            logs.logs_get_job_submission_history(ssh_conn, int(days) if days else 7)
        elif choice == "❌ Find Error Logs":
            logs.logs_get_error_logs(ssh_conn)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
