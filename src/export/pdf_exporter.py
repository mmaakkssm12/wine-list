import asyncio
import asyncmy
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
from fpdf import FPDF

class PDFExportWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, db_config, report_type, filename, company_name="WINESTORE", student_name=""):
        super().__init__()
        self.db_config = db_config
        self.report_type = report_type
        self.filename = filename
        self.company_name = company_name
        self.student_name = student_name
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if self.report_type == "statistical":
                result = loop.run_until_complete(self.generate_statistical_report())
            else:
                result = loop.run_until_complete(self.generate_detailed_report())
            
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
    
    async def get_connection(self):
        """Получение асинхронного соединения с БД"""
        return await asyncmy.connect(
            host=self.db_config['host'],
            user=self.db_config['user'],
            password=self.db_config['password'],
            db=self.db_config['db'],
            charset='utf8mb4'
        )
    
    async def fetch_wine_data(self):
        """Получение данных о винах"""
        try:
            conn = await self.get_connection()
            query = """
            SELECT wb.BottleID, wb.WineName, wb.Producer, wb.Vintage, 
                   wb.Region, wb.PurchasePrice, wb.PurchaseDate,
                   wl.Shelf, wl.Rack, wl.Cellar
            FROM WineBottle wb
            LEFT JOIN WineLocation wl ON wb.BottleID = wl.BottleID
            ORDER BY wb.BottleID DESC
            """
            
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                result = await cursor.fetchall()
            
            await conn.ensure_closed()
            return result
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
    
    async def fetch_statistical_data(self):
        """Получение статистических данных"""
        try:
            conn = await self.get_connection()
            
            # Общая статистика
            total_query = "SELECT COUNT(*) FROM WineBottle"
            value_query = "SELECT SUM(PurchasePrice) FROM WineBottle"
            region_query = "SELECT Region, COUNT(*) FROM WineBottle WHERE Region IS NOT NULL AND Region != '' GROUP BY Region"
            vintage_query = "SELECT Vintage, COUNT(*) FROM WineBottle WHERE Vintage IS NOT NULL GROUP BY Vintage ORDER BY Vintage"
            
            async with conn.cursor() as cursor:
                await cursor.execute(total_query)
                total_result = await cursor.fetchone()
                
                await cursor.execute(value_query)
                value_result = await cursor.fetchone()
                
                await cursor.execute(region_query)
                region_result = await cursor.fetchall()
                
                await cursor.execute(vintage_query)
                vintage_result = await cursor.fetchall()
            
            await conn.ensure_closed()
            
            return {
                'total_bottles': total_result[0] if total_result else 0,
                'total_value': float(value_result[0]) if value_result and value_result[0] else 0.0,
                'regions': dict(region_result) if region_result else {},
                'vintages': dict(vintage_result) if vintage_result else {}
            }
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {}
    
    async def generate_statistical_report(self):
        """Генерация статистического отчета"""
        try:
            # Получаем данные
            stats_data = await self.fetch_statistical_data()
            wine_data = await self.fetch_wine_data()
            
            # Создаем PDF
            pdf = StatisticalPDFReport(self.company_name, self.student_name)
            pdf.generate_report(stats_data, wine_data, self.filename)
            
            return self.filename
        except Exception as e:
            raise Exception(f"Ошибка генерации статистического отчета: {e}")
    
    async def generate_detailed_report(self):
        """Генерация детального отчета"""
        try:
            # Получаем данные
            wine_data = await self.fetch_wine_data()
            
            # Создаем PDF
            pdf = DetailedPDFReport(self.company_name, self.student_name)
            pdf.generate_report(wine_data, self.filename)
            
            return self.filename
        except Exception as e:
            raise Exception(f"Ошибка генерации детального отчета: {e}")

class PDFReportBase:
    """Базовый класс для генерации PDF отчетов с поддержкой кириллицы"""
    
    def __init__(self, company_name="WINESTORE", student_name=""):
        self.company_name = company_name
        self.student_name = student_name
        self.pdf = FPDF()
        self.setup_pdf()
        
    def setup_pdf(self):
        """Настройка PDF с поддержкой кириллицы"""
        # Добавляем поддержку кириллицы
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
    def _safe_text(self, text):
        """Безопасный вывод текста с поддержкой кириллицы"""
        if text is None:
            return ""
        # Заменяем только валютные символы, кириллицу оставляем как есть
        replacements = {
            '₽': 'RUB',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'JPY'
        }
        result = str(text)
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
    
    def header(self):
        """Заголовок страницы"""
        if self.pdf.page_no() == 1:
            return
            
        # Используем стандартный шрифт для заголовка
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 10, "WINESTORE - Report", 0, 1, "C")
        self.pdf.ln(5)
        
    def footer(self):
        """Нижний колонтитул"""
        self.pdf.set_y(-15)
        self.pdf.set_font("Arial", "I", 8)
        self.pdf.cell(0, 10, f"Page {self.pdf.page_no()}", 0, 0, "C")
        
    def create_title_page(self, title, subtitle=""):
        """Создание титульной страницы"""
        self.pdf.add_page()
        
        # Заголовок компании (латиницей)
        self.pdf.set_font("Arial", "B", 24)
        self.pdf.cell(0, 40, self.company_name, 0, 1, "C")
        
        # Основной заголовок (используем безопасный текст)
        self.pdf.set_font("Arial", "B", 18)
        safe_title = self._safe_text(title)
        self.pdf.cell(0, 20, safe_title, 0, 1, "C")
        
        if subtitle:
            self.pdf.set_font("Arial", "I", 14)
            safe_subtitle = self._safe_text(subtitle)
            self.pdf.cell(0, 15, safe_subtitle, 0, 1, "C")
            
        # Информация о дате и авторе (латиницей)
        self.pdf.set_font("Arial", "", 12)
        self.pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}", 0, 1, "C")
        
        if self.student_name:
            safe_student_name = self._safe_text(self.student_name)
            self.pdf.cell(0, 10, f"Student: {safe_student_name}", 0, 1, "C")
        else:
            self.pdf.cell(0, 10, "Author: WINESTORE Reporting System", 0, 1, "C")
            
        self.pdf.ln(20)
        
    def add_section_title(self, title, level=1):
        """Добавление заголовка раздела"""
        safe_title = self._safe_text(title)
        
        if level == 1:
            self.pdf.set_font("Arial", "B", 16)
            self.pdf.cell(0, 15, safe_title, 0, 1, "L")
            self.pdf.ln(5)
        elif level == 2:
            self.pdf.set_font("Arial", "B", 14)
            self.pdf.cell(0, 12, safe_title, 0, 1, "L")
            self.pdf.ln(3)
        else:
            self.pdf.set_font("Arial", "B", 12)
            self.pdf.cell(0, 10, safe_title, 0, 1, "L")
            self.pdf.ln(2)

class StatisticalPDFReport(PDFReportBase):
    """Генератор статистического отчета"""
    
    def generate_report(self, stats_data, wine_data, filename):
        """Генерация статистического отчета"""
        # Титульная страница
        self.create_title_page("General Application Statistics", 
                             "Statistical Report for Wine Collection")
        
        # Раздел 1: Общая статистика
        self.add_section_title("1. General Statistics", 1)
        
        self.pdf.set_font("Arial", "", 12)
        
        stats_text = f"""
        Total bottles in collection: {stats_data.get('total_bottles', 0)}
        Total collection value: {stats_data.get('total_value', 0):,.2f} RUB
        Number of regions: {len(stats_data.get('regions', {}))}
        """
        
        self.pdf.multi_cell(0, 8, stats_text.strip())
        self.pdf.ln(10)
        
        # Раздел 2: Распределение по регионам
        self.add_section_title("2. Distribution by Regions", 1)
        
        regions = stats_data.get('regions', {})
        if regions:
            for region, count in regions.items():
                safe_region = self._safe_text(region)
                self.pdf.cell(0, 8, f"- {safe_region}: {count} bottles", 0, 1)
        else:
            self.pdf.cell(0, 8, "No region data available", 0, 1)
            
        self.pdf.ln(10)
        
        # Раздел 3: Распределение по годам
        self.add_section_title("3. Distribution by Years", 1)
        
        vintages = stats_data.get('vintages', {})
        if vintages:
            for vintage, count in vintages.items():
                self.pdf.cell(0, 8, f"- {vintage}: {count} bottles", 0, 1)
        else:
            self.pdf.cell(0, 8, "No vintage data available", 0, 1)
            
        self.pdf.ln(10)
        
        # Раздел 4: Топ вин
        self.add_section_title("4. Top Wines by Value", 1)
        
        if wine_data:
            # Сортируем по цене и берем топ-5
            expensive_wines = sorted(wine_data, 
                                   key=lambda x: float(x[5]) if x[5] is not None else 0, 
                                   reverse=True)[:5]
            
            for i, wine in enumerate(expensive_wines, 1):
                wine_name = self._safe_text(wine[1])
                producer = self._safe_text(wine[2])
                price = float(wine[5]) if wine[5] is not None else 0
                self.pdf.cell(0, 8, f"{i}. {wine_name} - {producer} - {price:,.2f} RUB", 0, 1)
        else:
            self.pdf.cell(0, 8, "No wine data available", 0, 1)
            
        # Сохранение файла
        self.pdf.output(filename)

class DetailedPDFReport(PDFReportBase):
    """Генератор детального табличного отчета"""
    
    def generate_report(self, wine_data, filename):
        """Генерация детального отчета"""
        # Титульная страница
        self.create_title_page("Detailed Collection Information", 
                             "Complete Wine List with Detailed Information")
        
        # Раздел 1: Детальная информация о винах
        self.add_section_title("1. Detailed Wine Information", 1)
        
        if not wine_data:
            self.pdf.cell(0, 10, "No data available for report", 0, 1)
            self.pdf.output(filename)
            return
            
        # Создаем таблицу
        headers = ['ID', 'Name', 'Producer', 'Year', 'Region', 'Price']
        col_widths = [15, 40, 35, 15, 25, 25]
        
        # Заголовок таблицы
        self.pdf.set_fill_color(200, 200, 200)
        self.pdf.set_font("Arial", "B", 10)
        
        for i, header in enumerate(headers):
            self.pdf.cell(col_widths[i], 10, header, 1, 0, "C", True)
        self.pdf.ln()
        
        # Данные таблицы
        self.pdf.set_fill_color(255, 255, 255)
        self.pdf.set_font("Arial", "", 9)
        
        fill = False
        for row in wine_data:
            fill = not fill
            if fill:
                self.pdf.set_fill_color(245, 245, 245)
            else:
                self.pdf.set_fill_color(255, 255, 255)
                
            # ID
            self.pdf.cell(col_widths[0], 8, str(row[0]), 1, 0, "C", True)
            # Название
            wine_name = self._safe_text(row[1])
            if len(wine_name) > 30:
                wine_name = wine_name[:27] + "..."
            self.pdf.cell(col_widths[1], 8, wine_name, 1, 0, "L", True)
            # Производитель
            producer = self._safe_text(row[2])
            if len(producer) > 25:
                producer = producer[:22] + "..."
            self.pdf.cell(col_widths[2], 8, producer, 1, 0, "L", True)
            # Год
            self.pdf.cell(col_widths[3], 8, str(row[3]) if row[3] else "N/A", 1, 0, "C", True)
            # Регион
            region = self._safe_text(row[4])
            if len(region) > 20:
                region = region[:17] + "..."
            self.pdf.cell(col_widths[4], 8, region, 1, 0, "L", True)
            # Цена
            price = f"{float(row[5]):.2f}" if row[5] else "N/A"
            self.pdf.cell(col_widths[5], 8, price, 1, 0, "R", True)
            self.pdf.ln()
            
        self.pdf.ln(10)
        
        # Раздел 2: Сводная информация
        self.add_section_title("2. Summary Information", 1)
        
        total_bottles = len(wine_data)
        total_value = sum(float(row[5]) for row in wine_data if row[5] is not None)
        avg_price = total_value / total_bottles if total_bottles > 0 else 0
        
        summary = f"""
        Total number of bottles: {total_bottles}
        Total collection value: {total_value:,.2f} RUB
        Average bottle price: {avg_price:.2f} RUB
        """
        
        self.pdf.set_font("Arial", "", 12)
        self.pdf.multi_cell(0, 8, summary.strip())
        
        # Сохранение файла
        self.pdf.output(filename)
