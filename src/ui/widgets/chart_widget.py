from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt

class SimpleChartWidget(QWidget):
    def __init__(self, chart_type="line", data=None, title=""):
        super().__init__()
        self.chart_type = chart_type
        self.data = data or {'labels': [], 'values': []}
        self.title = title
        self.setMinimumHeight(200)
        self.setMinimumWidth(300)
        
    def set_data(self, data):
        """Установка данных для графика"""
        self.data = data or {'labels': [], 'values': []}
        self.update()
        
    def paintEvent(self, event):
        """Отрисовка графика"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Фон
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        if not self.data or not self.data.get('values'):
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Нет данных для отображения")
            return
            
        # Заголовок
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(10, 20, self.title)
        
        if self.chart_type == "line":
            self.draw_line_chart(painter)
        elif self.chart_type == "pie":
            self.draw_pie_chart(painter)
            
    def draw_line_chart(self, painter):
        """Отрисовка линейного графика"""
        values = self.data.get('values', [])
        labels = self.data.get('labels', [str(i) for i in range(len(values))])
        
        if not values:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Нет данных")
            return
            
        margin = 50
        chart_width = max(self.width() - 2 * margin, 100)
        chart_height = max(self.height() - 2 * margin, 100)
        
        max_value = max(values) if values else 1
        min_value = min(values) if values else 0
        value_range = max_value - min_value if max_value != min_value else 1
        
        # Оси
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawLine(margin, margin, margin, margin + chart_height)  # Y ось
        painter.drawLine(margin, margin + chart_height, margin + chart_width, margin + chart_height)  # X ось
        
        # Линия графика
        painter.setPen(QPen(QColor(65, 105, 225), 3))
        
        points = []
        for i, value in enumerate(values):
            x = margin + (i / max(len(values) - 1, 1)) * chart_width
            y = margin + chart_height - ((value - min_value) / value_range) * chart_height
            points.append((x, y))
            
        for i in range(len(points) - 1):
            painter.drawLine(int(points[i][0]), int(points[i][1]), 
                           int(points[i+1][0]), int(points[i+1][1]))
            
        # Точки и подписи
        painter.setPen(QPen(QColor(30, 144, 255), 8))
        for (x, y), label, value in zip(points, labels, values):
            painter.drawPoint(int(x), int(y))
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(int(x) - 10, int(y) - 10, f"{value}")
            painter.drawText(int(x) - 10, margin + chart_height + 20, str(label))
            
    def draw_pie_chart(self, painter):
        """Отрисовка круговой диаграммы"""
        values = self.data.get('values', [])
        labels = self.data.get('labels', [f"Категория {i}" for i in range(len(values))])
        
        total = sum(values)
        if total == 0:
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Нет данных")
            return
            
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 50
        
        colors = [QColor(255, 99, 132), QColor(54, 162, 235), QColor(255, 205, 86),
                 QColor(75, 192, 192), QColor(153, 102, 255), QColor(255, 159, 64)]
        
        start_angle = 0
        painter.setFont(QFont("Arial", 8))
        
        for i, (value, label) in enumerate(zip(values, labels)):
            angle = int(5760 * (value / total))  # 5760 = 360 * 16
            color = colors[i % len(colors)]
            
            # Сектор
            painter.setBrush(color)
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawPie(center_x - radius, center_y - radius, 
                           radius * 2, radius * 2, start_angle, angle)
            
            # Легенда
            legend_x = 10
            legend_y = 50 + i * 20
            painter.setBrush(color)
            painter.drawRect(legend_x, legend_y, 15, 15)
            percentage = (value / total) * 100 if total > 0 else 0
            painter.drawText(legend_x + 20, legend_y + 12, 
                           f"{label} ({value}, {percentage:.1f}%)")
            
            start_angle += angle
