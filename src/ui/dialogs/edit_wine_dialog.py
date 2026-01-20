from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                            QLineEdit, QDialogButtonBox, QMessageBox)
from datetime import datetime  # Добавляем импорт

class EditWineDialog(QDialog):
    def __init__(self, wine_data, parent=None):
        super().__init__(parent)
        self.wine_data = wine_data
        self.setWindowTitle("Редактирование записи")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit(self.wine_data['Varietal'])
        self.producer_input = QLineEdit(self.wine_data['Producer'])
        self.region_input = QLineEdit(self.wine_data['Region'])
        self.vintage_input = QLineEdit(str(self.wine_data['VintageYear']))
        self.price_input = QLineEdit(str(self.wine_data.get('Price', 0)))
        
        # Поле для даты покупки
        self.purchase_date_input = QLineEdit()
        if self.wine_data.get('PurchaseDate'):
            # Преобразуем дату в строку для отображения
            purchase_date = self.wine_data['PurchaseDate']
            # Проверяем, является ли purchase_date объектом с методом strftime
            if hasattr(purchase_date, 'strftime'):
                self.purchase_date_input.setText(purchase_date.strftime('%Y-%m-%d'))
            else:
                self.purchase_date_input.setText(str(purchase_date))
        
        # Поля местоположения
        self.shelf_input = QLineEdit(self.wine_data.get('Shelf', ''))
        self.rack_input = QLineEdit(self.wine_data.get('Rack', ''))
        self.cellar_input = QLineEdit(self.wine_data.get('Cellar', ''))
        
        form_layout.addRow("Название *:", self.name_input)
        form_layout.addRow("Производитель *:", self.producer_input)
        form_layout.addRow("Регион *:", self.region_input)
        form_layout.addRow("Год сбора урожая *:", self.vintage_input)
        form_layout.addRow("Цена (макс. 999999.99):", self.price_input)
        form_layout.addRow("Дата покупки (гггг-мм-дд):", self.purchase_date_input)
        form_layout.addRow("Полка:", self.shelf_input)
        form_layout.addRow("Стеллаж:", self.rack_input)
        form_layout.addRow("Погреб:", self.cellar_input)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def accept(self):
        """Проверка данных перед закрытием диалога"""
        # Проверяем обязательные поля
        if not all([self.name_input.text(), self.producer_input.text(), 
                   self.region_input.text(), self.vintage_input.text()]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля (отмечены *)")
            return
        
        # Проверяем числовые поля
        try:
            vintage = int(self.vintage_input.text())
            price = float(self.price_input.text()) if self.price_input.text() else 0
            
            if price > 999999.99:
                QMessageBox.warning(self, "Ошибка", "Цена не может превышать 999 999.99")
                return
                
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность числовых полей")
            return
        
        super().accept()
    
    def get_data(self):
        """Получение данных из формы"""
        return {
            'Varietal': self.name_input.text(),
            'Producer': self.producer_input.text(),
            'Region': self.region_input.text(),
            'VintageYear': int(self.vintage_input.text()) if self.vintage_input.text() else 0,
            'Price': float(self.price_input.text()) if self.price_input.text() else 0,
            'PurchaseDate': self.purchase_date_input.text(),
            'Shelf': self.shelf_input.text(),
            'Rack': self.rack_input.text(),
            'Cellar': self.cellar_input.text()
        }
