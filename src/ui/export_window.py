from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QMessageBox, QProgressBar, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from datetime import datetime
from ui.dialogs.export_dialog import ExportDialog
from export.pdf_exporter import PDFExportWorker
from export.excel_exporter import ExcelExportWorker

class ExportWindow(QWidget):
    def __init__(self, parent=None, db_config=None):
        super().__init__(parent)
        self.db_config = db_config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Экспорт данных коллекции")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Информация
        info = QLabel(
            "Модуль позволяет экспортировать данные винной коллекции в форматы PDF и Excel.\n"
            "Выберите тип отчета и нажмите кнопку для начала экспорта."
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setWordWrap(True)
        layout.addWidget(info)
        
        # Кнопки экспорта
        pdf_stats_btn = QPushButton("📊 Экспорт в PDF (Статистика)")
        pdf_stats_btn.setMinimumHeight(50)
        pdf_stats_btn.clicked.connect(lambda: self.export_data("PDF - Статистический отчет"))
        
        pdf_detail_btn = QPushButton("📋 Экспорт в PDF (Детальный)")
        pdf_detail_btn.setMinimumHeight(50)
        pdf_detail_btn.clicked.connect(lambda: self.export_data("PDF - Детальный отчет"))
        
        excel_btn = QPushButton("📈 Экспорт в Excel (Полный)")
        excel_btn.setMinimumHeight(50)
        excel_btn.clicked.connect(lambda: self.export_data("Excel - Полный отчет"))
        
        layout.addWidget(pdf_stats_btn)
        layout.addWidget(pdf_detail_btn)
        layout.addWidget(excel_btn)
        
        # Прогресс-бар
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Статус
        self.status = QLabel("Готов к экспорту данных")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status)
        
        self.setLayout(layout)
    
    def export_data(self, export_type):
        """Запуск экспорта данных"""
        try:
            # Диалог для ввода дополнительных параметров
            dialog = ExportDialog(self, self.db_config)
            if dialog.exec():
                params = dialog.get_export_params()
                student_name = params['student_name']
                
                # Выбор файла для сохранения
                if export_type.startswith("PDF"):
                    file_filter = "PDF Files (*.pdf)"
                    default_name = f"wine_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                else:
                    file_filter = "Excel Files (*.xlsx)"
                    default_name = f"wine_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
                
                filename, _ = QFileDialog.getSaveFileName(
                    self, "Сохранить отчет", default_name, file_filter
                )
                
                if filename:
                    self.start_export(export_type, filename, student_name)
                    
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при экспорте: {e}")
    
    def start_export(self, export_type, filename, student_name):
        """Запуск процесса экспорта"""
        try:
            self.status.setText("Подготовка к экспорту...")
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)  # Неопределенный прогресс
            
            if export_type.startswith("PDF"):
                if "Статистический" in export_type:
                    report_type = "statistical"
                else:
                    report_type = "detailed"
                    
                self.worker = PDFExportWorker(
                    self.db_config, report_type, filename, 
                    "WINESTORE", student_name
                )
            else:
                self.worker = ExcelExportWorker(
                    self.db_config, filename, "WINESTORE", student_name
                )
            
            self.worker.finished.connect(self.on_export_finished)
            self.worker.error.connect(self.on_export_error)
            self.worker.start()
            
        except Exception as e:
            self.on_export_error(str(e))
    
    def on_export_finished(self, filename):
        """Обработка успешного завершения экспорта"""
        self.progress.setVisible(False)
        self.status.setText(f"Экспорт завершен: {filename}")
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Экспорт завершен")
        msg.setText(f"Отчет успешно создан:\n{filename}")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def on_export_error(self, error_message):
        """Обработка ошибки экспорта"""
        self.progress.setVisible(False)
        self.status.setText("Ошибка экспорта")
        
        QMessageBox.warning(self, "Ошибка", f"Не удалось создать отчет:\n{error_message}")
