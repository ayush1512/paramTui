"""Main menu and connection menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.connection import SSHConnection


def connection_menu():
    """Initial menu to establish SSH connection."""
    console.clear()
    print_header()
    
    host = questionary.text(
        "🌐 Enter Host PARAM IP or Domain:",
        default="paramutkarsh.cdac.in",
        style=custom_style
    ).ask()
    if not host:
        return None
    
    user = questionary.text(
        "👤 Enter Username:",
        default="",
        style=custom_style
    ).ask()
    if not user:
        return None
    
    port = questionary.text(
        "🔌 Enter Port:",
        default="4422",
        style=custom_style
    ).ask()
    if not port:
        return None
    
    ssh_conn = SSHConnection()
    success = ssh_conn.connect(host, user, port)
    
    if success:
        return ssh_conn
    else:
        console.print("[bold red]Failed to connect. Exiting...[/bold red]")
        return None


def main_menu():
    """Main menu after SSH connection is established."""
    # Import here to avoid circular imports
    from manager.ui.file_manager import file_manager_menu
    from manager.ui.job_dashboard import job_dashboard_menu
    from manager.ui.job_templates import job_templates_menu
    from manager.ui.conda_manager import conda_menu
    from manager.ui.modules_menu import modules_menu
    from manager.ui.interactive import interactive_tools_menu
    from manager.ui.resources import resource_monitor_menu
    from manager.ui.quota import usage_quota_menu
    from manager.ui.logs_menu import logs_menu
    from manager.ui.settings_menu import settings_menu
    from manager.ui.help_menu import help_menu
    from manager.ui.tunnel_menu import tunnel_menu
    
    # Step 1: Establish SSH Connection
    ssh_conn = connection_menu()
    
    if not ssh_conn:
        return
    
    # Step 2: Show management options
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "🎯 What would you like to do?",
            choices=[
                questionary.Separator("─── Core Features ───"),
                "📁 File Manager",
                "📊 Job Dashboard",
                # "🧾 Job Templates",
                "🐍 Conda Package Manager",
                questionary.Separator("─── HPC Tools ───"),
                # "🧩 Software Modules",
                "🧠 Interactive Tools",
                "🖥️  Resource Monitor",
                questionary.Separator("─── System ───"),
                "📈 Usage & Quota",
                "🧪 Logs",
                "🔗 SSH Tunnel",
                "🖥️  Interactive Shell",
                questionary.Separator("─── Settings & Help ───"),
                "👤 User Settings",
                "📚 Help",
                questionary.Separator(),
                "🚪 Disconnect & Exit"
            ],
            style=custom_style
        ).ask()
        
        if choice == "📁 File Manager":
            file_manager_menu(ssh_conn)
        elif choice == "📊 Job Dashboard":
            job_dashboard_menu(ssh_conn)
        elif choice == "🧾 Job Templates":
            job_templates_menu(ssh_conn)
        elif choice == "🐍 Conda Package Manager":
            conda_menu(ssh_conn)
        elif choice == "🧩 Software Modules":
            modules_menu(ssh_conn)
        elif choice == "🧠 Interactive Tools":
            interactive_tools_menu(ssh_conn)
        elif choice == "🖥️  Resource Monitor":
            resource_monitor_menu(ssh_conn)
        elif choice == "📈 Usage & Quota":
            usage_quota_menu(ssh_conn)
        elif choice == "🧪 Logs":
            logs_menu(ssh_conn)
        elif choice == "🔗 SSH Tunnel":
            tunnel_menu(ssh_conn)
        elif choice == "🖥️  Interactive Shell":
            ssh_conn.interactive_shell()
            questionary.press_any_key_to_continue(style=custom_style).ask()
        elif choice == "👤 User Settings":
            settings_menu(ssh_conn)
        elif choice == "📚 Help":
            help_menu(ssh_conn)
        elif choice == "🚪 Disconnect & Exit":
            ssh_conn.disconnect()
            console.print("\n[bold yellow]👋 Goodbye! Thanks for using PARAM TUI.[/bold yellow]")
            break
