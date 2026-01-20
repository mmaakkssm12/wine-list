from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QTimer
from ui.dashboard import DashboardWindow
from ui.data_management import DataManagementWindow
from ui.search_window import SearchWindow
from ui.export_window import ExportWindow
from ui.reports_window import ReportsWindow
from ui.admin_window import AdminWindow
from ui.help_window import HelpWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_config = {
            'host': 'localhost',
            'user': 'maksim',
            'password': '12345',
            'db': 'is21-18'
        }
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("WINESTORE - Управление винной коллекцией")
        self.setGeometry(100, 100, 1400, 900)
        
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Создаем все окна
        self.dashboard_window = DashboardWindow(self)
        self.data_management_window = DataManagementWindow(self)
        self.search_window = SearchWindow(self)
        self.export_window = ExportWindow(self, self.db_config)
        self.reports_window = ReportsWindow(self)
        self.admin_window = AdminWindow(self)
        self.help_window = HelpWindow(self)
        
        # Добавляем окна в stacked widget
        self.central_widget.addWidget(self.dashboard_window)
        self.central_widget.addWidget(self.data_management_window)
        self.central_widget.addWidget(self.search_window)
        self.central_widget.addWidget(self.export_window)
        self.central_widget.addWidget(self.reports_window)
        self.central_widget.addWidget(self.admin_window)
        self.central_widget.addWidget(self.help_window)
        
        self.create_menu()
        self.show_dashboard()
    
    def create_menu(self):
        menubar = self.menuBar()
        
        # 🏠 Главная панель
        home_menu = menubar.addMenu('🏠 Главная панель')
        dashboard_action = QAction('📊 Дашборд', self)
        dashboard_action.triggered.connect(self.show_dashboard)
        home_menu.addAction(dashboard_action)
        
        # 👥 Управление данными
        data_menu = menubar.addMenu('👥 Управление данными')
        data_action = QAction('📝 Управление записями', self)
        data_action.triggered.connect(self.show_data_management)
        data_menu.addAction(data_action)
        
        # 🔍 Поиск и фильтрация
        search_menu = menubar.addMenu('🔍 Поиск и фильтрация')
        search_action = QAction('🔎 Поиск', self)
        search_action.triggered.connect(self.show_search)
        search_menu.addAction(search_action)
        
        # 📤 Экспорт данных
        export_menu = menubar.addMenu('📤 Экспорт данных')
        export_action = QAction('📊 Экспорт отчетов', self)
        export_action.triggered.connect(self.show_export)
        export_menu.addAction(export_action)
        
        # 📈 Отчеты и аналитика
        reports_menu = menubar.addMenu('📈 Отчеты и аналитика')
        reports_action = QAction('📋 Отчеты', self)
        reports_action.triggered.connect(self.show_reports)
        reports_menu.addAction(reports_action)
        
        # ⚙️ Администрирование
        admin_menu = menubar.addMenu('⚙️ Администрирование')
        admin_action = QAction('👤 Администрирование', self)
        admin_action.triggered.connect(self.show_admin)
        admin_menu.addAction(admin_action)
        
        # 🆘 Справка и поддержка
        help_menu = menubar.addMenu('🆘 Справка и поддержка')
        help_action = QAction('❓ Справка', self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        # Создаем меню Файл
        file_menu = menubar.addMenu('Файл')
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def show_dashboard(self):
        self.central_widget.setCurrentWidget(self.dashboard_window)
        self.setWindowTitle("WINESTORE - Главная панель")
        # Вызываем обновление дашборда с небольшой задержкой
        QTimer.singleShot(100, self.dashboard_window.on_update_dashboard)
    
    def show_data_management(self):
        self.central_widget.setCurrentWidget(self.data_management_window)
        self.setWindowTitle("WINESTORE - Управление данными")
    
    def show_search(self):
        self.central_widget.setCurrentWidget(self.search_window)
        self.setWindowTitle("WINESTORE - Поиск и фильтрация")
    
    def show_export(self):
        self.central_widget.setCurrentWidget(self.export_window)
        self.setWindowTitle("WINESTORE - Экспорт данных")
    
    def show_reports(self):
        self.central_widget.setCurrentWidget(self.reports_window)
        self.setWindowTitle("WINESTORE - Отчеты и аналитика")
    
    def show_admin(self):
        self.central_widget.setCurrentWidget(self.admin_window)
        self.setWindowTitle("WINESTORE - Администрирование")
    
    def show_help(self):
        self.central_widget.setCurrentWidget(self.help_window)
        self.setWindowTitle("WINESTORE - Справка и поддержка")
