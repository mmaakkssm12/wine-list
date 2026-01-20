from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QGroupBox, QComboBox,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from models.database import AsyncDatabaseManager, DatabaseWorker
from ui.widgets.chart_widget import SimpleChartWidget

class DashboardWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = AsyncDatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Верхний уровень меню дашборда
        dashboard_menu_layout = QHBoxLayout()
        
        overview_menu = QComboBox()
        overview_menu.addItems(["📊 Ключевые метрики", "📈 Динамика изменений", "🎪 Инфографика"])
        
        analysis_menu = QComboBox()
        analysis_menu.addItems(["📋 Детализированные данные", "🔄 Сравнительный анализ", "📅 Исторические данные"])
        
        settings_menu = QComboBox()
        settings_menu.addItems(["🎨 Темы оформления", "📏 Размеры элементов", "🔄 Обновление данных"])
        
        export_menu = QComboBox()
        export_menu.addItems(["💾 Сохранить как изображение", "📄 Экспорт в PDF", "📊 Выгрузка данных"])
        
        dashboard_menu_layout.addWidget(QLabel("🎯 Обзор показателей:"))
        dashboard_menu_layout.addWidget(overview_menu)
        dashboard_menu_layout.addWidget(QLabel("🔍 Детальный анализ:"))
        dashboard_menu_layout.addWidget(analysis_menu)
        dashboard_menu_layout.addWidget(QLabel("⚙️ Настройки:"))
        dashboard_menu_layout.addWidget(settings_menu)
        dashboard_menu_layout.addWidget(QLabel("📤 Экспорт:"))
        dashboard_menu_layout.addWidget(export_menu)
        
        main_layout.addLayout(dashboard_menu_layout)
        
        # Карточки с метриками
        metrics_layout = QHBoxLayout()
        
        self.metric_cards = {
            'total': self.create_metric_card("Всего бутылок", "0"),
            'storage': self.create_metric_card("В хранилище", "0"),
            'consumed': self.create_metric_card("Выпито", "0"),
            'value': self.create_metric_card("Стоимость коллекции", "₽0")
        }
        
        for card in self.metric_cards.values():
            metrics_layout.addWidget(card)
        
        main_layout.addLayout(metrics_layout)
        
        # Основная область с графиками и таблицами
        content_layout = QHBoxLayout()
        
        # Левая колонка - графики
        left_column = QVBoxLayout()
        
        # Линейный график
        line_chart_group = QGroupBox("📈 Динамика пополнения коллекции по годам")
        self.line_chart_layout = QVBoxLayout()
        self.line_chart = SimpleChartWidget("line", None, "Количество бутылок по годам урожая")
        self.line_chart_layout.addWidget(self.line_chart)
        line_chart_group.setLayout(self.line_chart_layout)
        left_column.addWidget(line_chart_group)
        
        # Круговая диаграмма
        pie_chart_group = QGroupBox("📊 Распределение по регионам")
        self.pie_chart_layout = QVBoxLayout()
        self.pie_chart = SimpleChartWidget("pie", None, "Распределение коллекции по регионам")
        self.pie_chart_layout.addWidget(self.pie_chart)
        pie_chart_group.setLayout(self.pie_chart_layout)
        left_column.addWidget(pie_chart_group)
        
        # Правая колонка - таблица
        right_column = QVBoxLayout()
        
        table_group = QGroupBox("📋 Последние добавленные вина")
        table_layout = QVBoxLayout()
        
        self.recent_wines_table = QTableWidget()
        self.recent_wines_table.setColumnCount(6)
        self.recent_wines_table.setHorizontalHeaderLabels(["Название", "Производитель", "Регион", "Год", "Местоположение", "Статус"])
        self.recent_wines_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_layout.addWidget(self.recent_wines_table)
        table_group.setLayout(table_layout)
        right_column.addWidget(table_group)
        
        content_layout.addLayout(left_column, 2)
        content_layout.addLayout(right_column, 1)
        
        main_layout.addLayout(content_layout)
        
        # Фильтры внизу
        filter_layout = QHBoxLayout()
        
        self.region_filter = QComboBox()
        self.region_filter.addItem("Все регионы")
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("Все статусы")
        self.status_filter.addItems(["В хранилище", "Выпито"])
        
        filter_layout.addWidget(QLabel("Регион:"))
        filter_layout.addWidget(self.region_filter)
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.status_filter)
        
        apply_filter_btn = QPushButton("Применить фильтры")
        apply_filter_btn.clicked.connect(self.on_apply_filters)
        filter_layout.addWidget(apply_filter_btn)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.on_update_dashboard)
        filter_layout.addWidget(refresh_btn)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        self.setLayout(main_layout)
        
        # Таймер для автоматического обновления каждые 30 секунд
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.on_update_dashboard)
        self.update_timer.start(30000)  # 30 секунд
        
        # Отложенная инициализация
        QTimer.singleShot(100, self.on_update_dashboard)
    
    def create_metric_card(self, name, value):
        card = QGroupBox(name)
        card_layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        
        card_layout.addWidget(value_label)
        card.setLayout(card_layout)
        
        return card
    
    def on_update_dashboard(self):
        """Запуск обновления дашборда"""
        self.update_dashboard()
    
    def on_apply_filters(self):
        """Запуск применения фильтров"""
        self.apply_filters()
    
    def update_dashboard(self):
        """Обновление дашборда"""
        try:
            self.worker = DatabaseWorker(self.db_manager.get_statistics)
            self.worker.finished.connect(self.on_stats_loaded)
            self.worker.error.connect(self.on_database_error)
            self.worker.start()
        except Exception as e:
            print(f"Ошибка обновления дашборда: {e}")
    
    def on_stats_loaded(self, stats):
        """Обработка загруженной статистики"""
        try:
            self.wine_worker = DatabaseWorker(self.db_manager.get_wine_bottles)
            self.wine_worker.finished.connect(lambda wines: self.finalize_stats_update(stats, wines))
            self.wine_worker.error.connect(self.on_database_error)
            self.wine_worker.start()
        except Exception as e:
            print(f"Ошибка обработки статистики: {e}")
    
    def finalize_stats_update(self, stats, wines):
        """Завершение обновления статистики с данными о винах"""
        # Обновляем карточки метрик
        self.metric_cards['total'].layout().itemAt(0).widget().setText(str(stats['total_bottles']))
        self.metric_cards['storage'].layout().itemAt(0).widget().setText(str(stats['in_storage']))
        self.metric_cards['consumed'].layout().itemAt(0).widget().setText(str(stats['consumed']))
        self.metric_cards['value'].layout().itemAt(0).widget().setText(f"₽{stats['total_value']:,.2f}")
        
        # Обновляем графики
        self.line_chart.set_data(stats['line_data'])
        self.pie_chart.set_data(stats['pie_data'])
        
        # Обновляем фильтр регионов
        current_region = self.region_filter.currentText()
        self.region_filter.clear()
        self.region_filter.addItem("Все регионы")
        regions = list(set(wine['Region'] for wine in wines if wine['Region']))
        self.region_filter.addItems(regions)
        
        # Восстанавливаем выбранный регион если он еще существует
        if current_region in regions:
            self.region_filter.setCurrentText(current_region)
        
        # Обновляем таблицу
        self.update_recent_wines_table(wines[-5:] if wines else [])
    
    def apply_filters(self):
        """Применение фильтров"""
        filters = {}
        
        if self.region_filter.currentText() != "Все регионы":
            filters['region'] = self.region_filter.currentText()
        
        if self.status_filter.currentText() != "Все статусы":
            pass
        
        self.filter_worker = DatabaseWorker(self.db_manager.search_wines, "", filters)
        self.filter_worker.finished.connect(lambda wines: self.update_recent_wines_table(wines[-5:] if wines else []))
        self.filter_worker.error.connect(self.on_database_error)
        self.filter_worker.start()
    
    def update_recent_wines_table(self, wines):
        self.recent_wines_table.setRowCount(len(wines))
        
        for row, wine in enumerate(wines):
            self.recent_wines_table.setItem(row, 0, QTableWidgetItem(wine['Varietal']))
            self.recent_wines_table.setItem(row, 1, QTableWidgetItem(wine['Producer']))
            self.recent_wines_table.setItem(row, 2, QTableWidgetItem(wine['Region']))
            self.recent_wines_table.setItem(row, 3, QTableWidgetItem(str(wine['VintageYear'])))
            
            # Показываем местоположение
            location = ""
            if wine.get('Cellar'):
                location += f"Погреб: {wine['Cellar']}"
            if wine.get('Rack'):
                location += f", Стеллаж: {wine['Rack']}"
            if wine.get('Shelf'):
                location += f", Полка: {wine['Shelf']}"
            if not location:
                location = "Не указано"
                
            self.recent_wines_table.setItem(row, 4, QTableWidgetItem(location))
            self.recent_wines_table.setItem(row, 5, QTableWidgetItem("В хранилище"))
    
    def on_database_error(self, error_message):
        """Обработка ошибок базы данных"""
        QMessageBox.warning(self, "Ошибка базы данных", f"Не удалось загрузить данные: {error_message}")
