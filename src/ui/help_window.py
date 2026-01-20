from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class HelpWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Справка и поддержка")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Информация
        info = QTextEdit()
        info.setReadOnly(True)
        info.setHtml("""
        <h2>Руководство пользователя WINESTORE</h2>
        
        <h3>Основные функции:</h3>
        <ul>
        <li><b>Главная панель</b> - просмотр статистики и дашборда</li>
        <li><b>Управление данными</b> - добавление, редактирование, просмотр и удаление записей о винах</li>
        <li><b>Поиск и фильтрация</b> - поиск вин по различным критериям</li>
        <li><b>Экспорт данных</b> - генерация отчетов в форматах PDF и Excel</li>
        <li><b>Отчеты и аналитика</b> - информация о доступных отчетах</li>
        <li><b>Администрирование</b> - управление системой</li>
        </ul>
        
        <h3>Экспорт отчетов:</h3>
        <p>Система поддерживает три типа отчетов:</p>
        <ol>
        <li><b>PDF - Статистический отчет</b>: Общая статистика коллекции</li>
        <li><b>PDF - Детальный отчет</b>: Полный список всех вин</li>
        <li><b>Excel - Полный отчет</b>: Комплексный отчет с графиками и аналитикой</li>
        </ol>
        
        <h3>Требования к системе:</h3>
        <ul>
        <li>Python 3.8+</li>
        <li>MySQL база данных</li>
        <li>Библиотеки: PyQt6, asyncmy, xlsxwriter, fpdf2</li>
        </ul>
        
        <p><i>По вопросам технической поддержки обращайтесь к администратору системы.</i></p>
        """)
        layout.addWidget(info)
        
        self.setLayout(layout)
