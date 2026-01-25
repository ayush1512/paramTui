"""Usage & Quota menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import resources


def usage_quota_menu(ssh_conn):
    """Usage & Quota submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "📈 Usage & Quota:",
            choices=[
                "💾 Disk Quota Usage",
                # "⚡ Compute Usage (CPU/GPU Hours)",
                # "⚠️  Check Quota Warnings",
                "📊 Remote System Info",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "💾 Disk Quota Usage":
            resources.quota_disk_usage(ssh_conn)
        # elif choice == "⚡ Compute Usage (CPU/GPU Hours)":
        #     resources.quota_compute_usage(ssh_conn)
        # elif choice == "⚠️  Check Quota Warnings":
        #     resources.quota_check_warnings(ssh_conn)
        elif choice == "📊 Remote System Info":
            resources.get_remote_system_info(ssh_conn)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
