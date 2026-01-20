from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                            QLineEdit, QComboBox, QDialogButtonBox)

class ExportDialog(QDialog):
    def __init__(self, parent=None, db_config=None):
        super().__init__(parent)
        self.db_config = db_config
        self.setWindowTitle("Экспорт данных")
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        self.export_type = QComboBox()
        self.export_type.addItems(["PDF - Статистический отчет", "PDF - Детальный отчет", "Excel - Полный отчет"])
        
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("ФИО студента (необязательно)")
        
        form_layout.addRow("Тип отчета:", self.export_type)
        form_layout.addRow("ФИО студента:", self.student_name)
        
        layout.addLayout(form_layout)
        
        # Кнопки
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_export_params(self):
        """Получение параметров экспорта"""
        export_type_text = self.export_type.currentText()
        
        if "Статистический" in export_type_text:
            report_type = "statistical"
        elif "Детальный" in export_type_text:
            report_type = "detailed"
        else:
            report_type = "excel"
        
        return {
            'export_type': export_type_text,
            'report_type': report_type,
            'student_name': self.student_name.text()
        }
