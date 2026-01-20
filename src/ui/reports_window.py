from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class ReportsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Отчеты и аналитика")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Информация
        info = QLabel(
            "В этом разделе доступны различные отчеты и аналитика по вашей винной коллекции.\n"
            "Для генерации отчетов перейдите в раздел 'Экспорт данных'."
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Примеры отчетов
        reports_group = QGroupBox("Доступные отчеты")
        reports_layout = QVBoxLayout()
        
        reports_list = [
            "📊 Статистический отчет - общая информация о коллекции",
            "📋 Детальный отчет - полный список всех вин",
            "📈 Excel отчет - комплексный отчет с графиками и аналитикой",
            "📅 Отчет по периодам - динамика изменений коллекции",
            "🏆 Топ-10 самых ценных вин"
        ]
        
        for report in reports_list:
            label = QLabel(report)
            reports_layout.addWidget(label)
        
        reports_group.setLayout(reports_layout)
        layout.addWidget(reports_group)
        
        self.setLayout(layout)
