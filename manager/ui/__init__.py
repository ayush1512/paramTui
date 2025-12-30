"""UI subpackage - Menu interfaces for ParamTUI."""

from manager.ui.styles import custom_style, print_header, console
from manager.ui.menus import main_menu, connection_menu
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
