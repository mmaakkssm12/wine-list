import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Класс для конфигурации приложения"""
    
    # Настройки базы данных
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'maksim')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '12345')
    DB_NAME = os.getenv('DB_NAME', 'is21-18')
    DB_CHARSET = os.getenv('DB_CHARSET', 'utf8mb4')
    
    # Настройки приложения
    APP_NAME = os.getenv('APP_NAME', 'WINESTORE')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    STUDENT_NAME = os.getenv('STUDENT_NAME', '')
    
    # Пути
    REPORTS_DIR = 'reports'
    EXPORTS_DIR = 'exports'
    
    @staticmethod
    def setup_directories():
        """Создание необходимых директорий"""
        directories = [Config.REPORTS_DIR, Config.EXPORTS_DIR]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    @staticmethod
    def get_db_config():
        """Получение конфигурации базы данных"""
        return {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'db': Config.DB_NAME,
            'charset': Config.DB_CHARSET
        }
    
    @staticmethod
    def get_app_info():
        """Получение информации о приложении"""
        return {
            'name': Config.APP_NAME,
            'version': Config.APP_VERSION,
            'student_name': Config.STUDENT_NAME
        }
    
    @staticmethod
    def validate_config():
        """Проверка конфигурации"""
        errors = []
        
        if not Config.DB_HOST:
            errors.append("DB_HOST не указан")
        if not Config.DB_USER:
            errors.append("DB_USER не указан")
        if not Config.DB_NAME:
            errors.append("DB_NAME не указан")
        
        return errors
