"""Resource Monitor menu."""

import questionary
from manager.ui.styles import custom_style, print_header, console
from manager.commands import resources


def resource_monitor_menu(ssh_conn):
    """Resource Monitor submenu."""
    while True:
        console.clear()
        print_header(ssh_conn)
        
        choice = questionary.select(
            "Resource Monitor:",
            choices=[
                "CPU Usage",
                "Memory Usage",
                "GPU Utilization",
                "Node Availability",
                questionary.Separator(),
                "← Back to Main Menu"
            ],
            style=custom_style
        ).ask()
        
        if choice == "CPU Usage":
            resources.resource_cpu_usage(ssh_conn)
        elif choice == "Memory Usage":
            resources.resource_memory_usage(ssh_conn)
        elif choice == "GPU Utilization":
            resources.resource_gpu_usage(ssh_conn)
        elif choice == "Node Availability":
            resources.resource_node_availability(ssh_conn)
        elif choice == "← Back to Main Menu":
            break
        
        if choice != "← Back to Main Menu":
            questionary.press_any_key_to_continue(style=custom_style).ask()
