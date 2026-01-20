"""
WINESTORE - Управление винной коллекцией
Точка входа приложения
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow
from utils.config import Config

def setup_environment():
    """Настройка окружения приложения"""
    try:
        # Создание необходимых директорий
        Config.setup_directories()
        
        # Проверка конфигурации
        errors = Config.validate_config()
        if errors:
            print("Ошибки конфигурации:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    except Exception as e:
        print(f"Ошибка настройки окружения: {e}")
        return False

def main():
    """Основная функция запуска приложения"""
    try:
        # Настройка окружения
        if not setup_environment():
            print("Не удалось настроить окружение приложения")
            return 1
        
        # Создание приложения Qt
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Установка иконки приложения (если есть)
        if os.path.exists("icon.ico"):
            app.setWindowIcon(QIcon("icon.ico"))
        
        # Создание и настройка главного окна
        window = MainWindow()
        window.show()
        
        # Запуск главного цикла приложения
        return_code = app.exec()
        
        print("Приложение завершено")
        return return_code
        
    except Exception as e:
        print(f"Критическая ошибка при запуске приложения: {e}")
        
        # Показать сообщение об ошибке если возможно
        try:
            error_app = QApplication([])
            QMessageBox.critical(None, "Критическая ошибка", 
                               f"Не удалось запустить приложение:\n{str(e)}")
        except:
            pass
            
        return 1

if __name__ == '__main__':
    sys.exit(main())
