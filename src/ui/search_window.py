from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QTabWidget, QFormLayout, QLineEdit, 
                            QComboBox, QSpinBox)
from PyQt6.QtCore import QTimer
from models.database import AsyncDatabaseManager, DatabaseWorker

class SearchWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = AsyncDatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # 🔎 Быстрый поиск
        quick_tab = QWidget()
        quick_layout = QVBoxLayout()
        
        quick_search_layout = QHBoxLayout()
        self.quick_search_input = QLineEdit()
        self.quick_search_input.setPlaceholderText("Введите название, производителя или регион...")
        quick_search_btn = QPushButton("🔎 Быстрый поиск")
        quick_search_btn.clicked.connect(self.on_quick_search)
        quick_search_layout.addWidget(self.quick_search_input)
        quick_search_layout.addWidget(quick_search_btn)
        quick_layout.addLayout(quick_search_layout)
        
        self.quick_results_table = QTableWidget()
        self.quick_results_table.setColumnCount(6)
        self.quick_results_table.setHorizontalHeaderLabels([
            "Название", "Производитель", "Регион", "Год", "Цена", "Местоположение"
        ])
        self.quick_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        quick_layout.addWidget(self.quick_results_table)
        
        quick_tab.setLayout(quick_layout)
        tabs.addTab(quick_tab, "🔎 Быстрый поиск")
        
        # ⚙️ Расширенный поиск
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout()
        
        advanced_form = QFormLayout()
        self.adv_name_input = QLineEdit()
        self.adv_producer_input = QLineEdit()
        self.adv_region_input = QLineEdit()
        self.adv_min_year = QSpinBox()
        self.adv_min_year.setRange(1900, 2030)
        self.adv_max_year = QSpinBox()
        self.adv_max_year.setRange(1900, 2030)
        self.adv_max_year.setValue(2030)
        
        advanced_form.addRow("Название:", self.adv_name_input)
        advanced_form.addRow("Производитель:", self.adv_producer_input)
        advanced_form.addRow("Регион:", self.adv_region_input)
        advanced_form.addRow("Год от:", self.adv_min_year)
        advanced_form.addRow("Год до:", self.adv_max_year)
        
        advanced_layout.addLayout(advanced_form)
        
        advanced_search_btn = QPushButton("⚙️ Расширенный поиск")
        advanced_search_btn.clicked.connect(self.on_advanced_search)
        advanced_layout.addWidget(advanced_search_btn)
        
        self.advanced_results_table = QTableWidget()
        self.advanced_results_table.setColumnCount(6)
        self.advanced_results_table.setHorizontalHeaderLabels([
            "Название", "Производитель", "Регион", "Год", "Цена", "Местоположение"
        ])
        self.advanced_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        advanced_layout.addWidget(self.advanced_results_table)
        
        advanced_tab.setLayout(advanced_layout)
        tabs.addTab(advanced_tab, "⚙️ Расширенный поиск")
        
        # 📑 Фильтры по категориям
        filters_tab = QWidget()
        filters_layout = QVBoxLayout()
        
        filters_form = QFormLayout()
        self.filter_region = QComboBox()
        self.filter_region.addItem("Все регионы")
        
        filters_form.addRow("Регион:", self.filter_region)
        
        filters_layout.addLayout(filters_form)
        
        filter_btn = QPushButton("📑 Применить фильтры")
        filter_btn.clicked.connect(self.on_apply_category_filters)
        filters_layout.addWidget(filter_btn)
        
        self.filter_results_table = QTableWidget()
        self.filter_results_table.setColumnCount(6)
        self.filter_results_table.setHorizontalHeaderLabels([
            "Название", "Производитель", "Регион", "Год", "Цена", "Местоположение"
        ])
        self.filter_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        filters_layout.addWidget(self.filter_results_table)
        
        filters_tab.setLayout(filters_layout)
        tabs.addTab(filters_tab, "📑 Фильтры по категориям")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Загружаем регионы для фильтра
        QTimer.singleShot(100, self.on_load_regions)
    
    def on_quick_search(self):
        self.quick_search()
    
    def on_advanced_search(self):
        self.advanced_search()
    
    def on_apply_category_filters(self):
        self.apply_category_filters()
    
    def on_load_regions(self):
        self.load_regions()
    
    def load_regions(self):
        self.region_worker = DatabaseWorker(self.db_manager.get_wine_bottles)
        self.region_worker.finished.connect(self.display_regions)
        self.region_worker.error.connect(lambda e: print(f"Ошибка загрузки регионов: {e}"))
        self.region_worker.start()
    
    def display_regions(self, wines):
        regions = list(set(wine['Region'] for wine in wines if wine['Region']))
        
        self.filter_region.clear()
        self.filter_region.addItem("Все регионы")
        self.filter_region.addItems(regions)
    
    def quick_search(self):
        search_term = self.quick_search_input.text()
        self.search_worker = DatabaseWorker(self.db_manager.search_wines, search_term)
        self.search_worker.finished.connect(lambda results: self.display_results(results, self.quick_results_table))
        self.search_worker.error.connect(lambda e: print(f"Ошибка поиска: {e}"))
        self.search_worker.start()
    
    def advanced_search(self):
        filters = {}
        if self.adv_name_input.text():
            filters['name'] = self.adv_name_input.text()
        if self.adv_producer_input.text():
            filters['producer'] = self.adv_producer_input.text()
        if self.adv_region_input.text():
            filters['region'] = self.adv_region_input.text()
        if self.adv_min_year.value() > 1900:
            filters['min_year'] = self.adv_min_year.value()
        if self.adv_max_year.value() < 2030:
            filters['max_year'] = self.adv_max_year.value()
        
        self.search_worker = DatabaseWorker(self.db_manager.search_wines, "", filters)
        self.search_worker.finished.connect(lambda results: self.display_results(results, self.advanced_results_table))
        self.search_worker.error.connect(lambda e: print(f"Ошибка поиска: {e}"))
        self.search_worker.start()
    
    def apply_category_filters(self):
        filters = {}
        if self.filter_region.currentText() != "Все регионы":
            filters['region'] = self.filter_region.currentText()
        
        self.search_worker = DatabaseWorker(self.db_manager.search_wines, "", filters)
        self.search_worker.finished.connect(lambda results: self.display_results(results, self.filter_results_table))
        self.search_worker.error.connect(lambda e: print(f"Ошибка поиска: {e}"))
        self.search_worker.start()
    
    def display_results(self, results, table):
        table.setRowCount(len(results))
        
        for row, wine in enumerate(results):
            table.setItem(row, 0, QTableWidgetItem(wine['Varietal']))
            table.setItem(row, 1, QTableWidgetItem(wine['Producer']))
            table.setItem(row, 2, QTableWidgetItem(wine['Region']))
            table.setItem(row, 3, QTableWidgetItem(str(wine['VintageYear'])))
            table.setItem(row, 4, QTableWidgetItem(str(wine.get('Price', 0))))
            
            # Добавляем местоположение
            location = ""
            if wine.get('Cellar'):
                location += f"Погреб: {wine['Cellar']}"
            if wine.get('Rack'):
                location += f", Стеллаж: {wine['Rack']}"
            if wine.get('Shelf'):
                location += f", Полка: {wine['Shelf']}"
            if not location:
                location = "Не указано"
                
            table.setItem(row, 5, QTableWidgetItem(location))
