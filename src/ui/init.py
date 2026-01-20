"""
Пользовательский интерфейс приложения WINESTORE
"""

from .main_window import MainWindow
from .dashboard import DashboardWindow
from .data_management import DataManagementWindow
from .search_window import SearchWindow
from .export_window import ExportWindow
from .reports_window import ReportsWindow
from .admin_window import AdminWindow
from .help_window import HelpWindow

__all__ = [
    'MainWindow',
    'DashboardWindow',
    'DataManagementWindow',
    'SearchWindow',
    'ExportWindow',
    'ReportsWindow',
    'AdminWindow',
    'HelpWindow'
]
