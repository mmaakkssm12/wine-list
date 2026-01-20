from datetime import datetime  # Добавьте этот импорт
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QMessageBox, QGroupBox, QComboBox,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QTabWidget, QFormLayout, QLineEdit)
from PyQt6.QtCore import QTimer
from models.database import AsyncDatabaseManager, DatabaseWorker
from ui.dialogs.edit_wine_dialog import EditWineDialog

class DataManagementWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_manager = AsyncDatabaseManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # 📝 Добавить запись
        add_tab = QWidget()
        add_layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.producer_input = QLineEdit()
        self.region_input = QLineEdit()
        self.vintage_input = QLineEdit()
        self.price_input = QLineEdit()
        self.purchase_date_input = QLineEdit()
        self.purchase_date_input.setPlaceholderText("гггг-мм-дд")
        
        # Поля местоположения
        self.shelf_input = QLineEdit()
        self.rack_input = QLineEdit()
        self.cellar_input = QLineEdit()
        
        form_layout.addRow("Название *:", self.name_input)
        form_layout.addRow("Производитель *:", self.producer_input)
        form_layout.addRow("Регион *:", self.region_input)
        form_layout.addRow("Год сбора урожая *:", self.vintage_input)
        form_layout.addRow("Цена (макс. 999999.99):", self.price_input)
        form_layout.addRow("Дата покупки (гггг-мм-дд):", self.purchase_date_input)
        form_layout.addRow("Полка:", self.shelf_input)
        form_layout.addRow("Стеллаж:", self.rack_input)
        form_layout.addRow("Погреб:", self.cellar_input)
        
        add_layout.addLayout(form_layout)
        
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        cancel_btn = QPushButton("Очистить")
        
        save_btn.clicked.connect(self.on_save_record)
        cancel_btn.clicked.connect(self.clear_form)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        add_layout.addLayout(buttons_layout)
        
        add_tab.setLayout(add_layout)
        tabs.addTab(add_tab, "📝 Добавить запись")
        
        # 👁️ Просмотр и редактирование записей
        view_tab = QWidget()
        view_layout = QVBoxLayout()
        
        # Заголовок с информацией
        info_label = QLabel("Все записи отображаются ниже. Для редактирования дважды щелкните по строке.")
        info_label.setStyleSheet("background-color: #e3f2fd; padding: 8px; border-radius: 4px;")
        view_layout.addWidget(info_label)
        
        view_filter_layout = QHBoxLayout()
        
        self.view_region_filter = QComboBox()
        self.view_region_filter.addItem("Все регионы")
        
        view_filter_layout.addWidget(QLabel("Регион:"))
        view_filter_layout.addWidget(self.view_region_filter)
        
        apply_view_filter_btn = QPushButton("Применить фильтры")
        apply_view_filter_btn.clicked.connect(self.on_apply_view_filters)
        view_filter_layout.addWidget(apply_view_filter_btn)
        
        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.on_load_view_records)
        view_filter_layout.addWidget(refresh_btn)
        
        view_layout.addLayout(view_filter_layout)
        
        self.view_records_table = QTableWidget()
        self.view_records_table.setColumnCount(9)
        self.view_records_table.setHorizontalHeaderLabels([
            "ID", "Название", "Производитель", "Регион", "Год", "Цена", "Дата покупки", "Местоположение", "Действия"
        ])
        self.view_records_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.view_records_table.doubleClicked.connect(self.edit_selected_record)
        view_layout.addWidget(self.view_records_table)
        
        # Кнопки управления
        action_layout = QHBoxLayout()
        edit_btn = QPushButton("✏️ Редактировать выбранное")
        delete_btn = QPushButton("🗑️ Удалить выбранное")
        
        edit_btn.clicked.connect(self.edit_selected_record)
        delete_btn.clicked.connect(self.delete_selected_records)
        
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(delete_btn)
        action_layout.addStretch()
        
        view_layout.addLayout(action_layout)
        
        view_tab.setLayout(view_layout)
        tabs.addTab(view_tab, "👁️ Просмотр и редактирование")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Отложенная загрузка данных
        QTimer.singleShot(100, self.on_load_view_records)
    
    def on_save_record(self):
        self.save_record()
    
    def on_load_view_records(self):
        self.load_view_records()
    
    def on_apply_view_filters(self):
        self.apply_view_filters()
    
    def save_record(self):
        required_fields = [self.name_input.text(), self.producer_input.text(), 
                          self.region_input.text(), self.vintage_input.text()]
        
        if not all(required_fields):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля (отмечены *)")
            return
        
        try:
            vintage_year = int(self.vintage_input.text())
            price = float(self.price_input.text()) if self.price_input.text() else 0
            
            # Проверка максимальной цены
            if price > 999999.99:
                QMessageBox.warning(self, "Ошибка", "Цена не может превышать 999 999.99")
                return
                
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность числовых полей")
            return
        
        data = {
            'name': self.name_input.text(),
            'producer': self.producer_input.text(),
            'region': self.region_input.text(),
            'vintage_year': vintage_year,
            'price': price,
            'purchase_date': self.purchase_date_input.text(),
            'shelf': self.shelf_input.text(),
            'rack': self.rack_input.text(),
            'cellar': self.cellar_input.text()
        }
        
        self.save_worker = DatabaseWorker(self.db_manager.add_wine_bottle, data)
        self.save_worker.finished.connect(self.on_save_complete)
        self.save_worker.error.connect(self.on_save_error)
        self.save_worker.start()
    
    def on_save_complete(self, success):
        if success:
            QMessageBox.information(self, "Успех", "Запись успешно добавлена")
            self.clear_form()
            self.load_view_records()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось добавить запись")
    
    def on_save_error(self, error_message):
        QMessageBox.warning(self, "Ошибка", f"Ошибка при сохранении: {error_message}")
    
    def clear_form(self):
        self.name_input.clear()
        self.producer_input.clear()
        self.region_input.clear()
        self.vintage_input.clear()
        self.price_input.clear()
        self.purchase_date_input.clear()
        self.shelf_input.clear()
        self.rack_input.clear()
        self.cellar_input.clear()
    
    def load_view_records(self, filters=None):
        self.load_worker = DatabaseWorker(self.db_manager.get_wine_bottles)
        self.load_worker.finished.connect(lambda wines: self.display_view_records(wines, filters))
        self.load_worker.error.connect(self.on_load_error)
        self.load_worker.start()
    
    def display_view_records(self, wines, filters=None):
        if filters:
            wines = [w for w in wines if not filters.get('region') or w['Region'] == filters['region']]
        
        self.view_records_table.setRowCount(len(wines))
        
        # Обновляем фильтр регионов
        current_region = self.view_region_filter.currentText()
        self.view_region_filter.clear()
        self.view_region_filter.addItem("Все регионы")
        regions = list(set(wine['Region'] for wine in wines if wine['Region']))
        self.view_region_filter.addItems(regions)
        
        # Восстанавливаем выбранный регион если он еще существует
        if current_region in regions:
            self.view_region_filter.setCurrentText(current_region)
        
        for row, wine in enumerate(wines):
            self.view_records_table.setItem(row, 0, QTableWidgetItem(str(wine['BottleID'])))
            self.view_records_table.setItem(row, 1, QTableWidgetItem(wine['Varietal']))
            self.view_records_table.setItem(row, 2, QTableWidgetItem(wine['Producer']))
            self.view_records_table.setItem(row, 3, QTableWidgetItem(wine['Region']))
            self.view_records_table.setItem(row, 4, QTableWidgetItem(str(wine['VintageYear'])))
            self.view_records_table.setItem(row, 5, QTableWidgetItem(str(wine.get('Price', 0))))
            
            # Добавляем дату покупки
            purchase_date = wine.get('PurchaseDate', '')
            if purchase_date:
                # Проверяем тип объекта - может быть datetime, date или строка
                if hasattr(purchase_date, 'strftime'):  # Если это datetime/date объект
                    purchase_date_str = purchase_date.strftime('%Y-%m-%d')
                else:
                    purchase_date_str = str(purchase_date)
            else:
                purchase_date_str = ''
            self.view_records_table.setItem(row, 6, QTableWidgetItem(purchase_date_str))
            
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
                
            self.view_records_table.setItem(row, 7, QTableWidgetItem(location))
            
            # Кнопка действий
            action_btn = QPushButton("✏️")
            action_btn.clicked.connect(lambda checked, r=row: self.edit_record_by_row(r))
            self.view_records_table.setCellWidget(row, 8, action_btn)
    
    def on_load_error(self, error_message):
        QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить данные: {error_message}")
    
    def apply_view_filters(self):
        filters = {}
        
        if self.view_region_filter.currentText() != "Все регионы":
            filters['region'] = self.view_region_filter.currentText()
        
        self.load_view_records(filters)
    
    def edit_record_by_row(self, row):
        bottle_id = int(self.view_records_table.item(row, 0).text())
        self.open_edit_dialog(bottle_id)
    
    def edit_selected_record(self):
        selected_items = self.view_records_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")
            return
        
        row = selected_items[0].row()
        bottle_id = int(self.view_records_table.item(row, 0).text())
        self.open_edit_dialog(bottle_id)
    
    def open_edit_dialog(self, bottle_id):
        self.edit_worker = DatabaseWorker(self.db_manager.get_wine_bottles)
        self.edit_worker.finished.connect(lambda wines: self.show_edit_dialog(wines, bottle_id))
        self.edit_worker.error.connect(self.on_load_error)
        self.edit_worker.start()
    
    def show_edit_dialog(self, wines, bottle_id):
        wine = next((w for w in wines if w['BottleID'] == bottle_id), None)
        
        if not wine:
            QMessageBox.warning(self, "Ошибка", "Запись не найдена")
            return
        
        dialog = EditWineDialog(wine, self)
        if dialog.exec():
            updated_data = dialog.get_data()
            self.update_worker = DatabaseWorker(self.db_manager.update_wine_bottle, bottle_id, updated_data)
            self.update_worker.finished.connect(self.on_update_complete)
            self.update_worker.error.connect(self.on_save_error)
            self.update_worker.start()
    
    def on_update_complete(self, success):
        if success:
            QMessageBox.information(self, "Успех", "Запись успешно обновлена")
            self.load_view_records()
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось обновить запись")
    
    def delete_selected_records(self):
        selected_items = self.view_records_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите записи для удаления")
            return
        
        bottle_ids = set()
        for item in selected_items:
            if item.column() == 0:  # ID в первом столбце
                bottle_ids.add(int(item.text()))
        
        reply = QMessageBox.question(self, "Подтверждение удаления", 
                                   f"Вы уверены, что хотите удалить {len(bottle_ids)} записей?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_records(bottle_ids)
    
    def delete_records(self, bottle_ids):
        self.delete_worker = DatabaseWorker(self.delete_records_async, bottle_ids)
        self.delete_worker.finished.connect(self.on_delete_complete)
        self.delete_worker.error.connect(self.on_save_error)
        self.delete_worker.start()
    
    async def delete_records_async(self, bottle_ids):
        success_count = 0
        for bottle_id in bottle_ids:
            if await self.db_manager.delete_wine_bottle(bottle_id):
                success_count += 1
        return success_count
    
    def on_delete_complete(self, success_count):
        QMessageBox.information(self, "Результат", f"Удалено {success_count} записей")
        self.load_view_records()
