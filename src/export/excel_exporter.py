import asyncio
import asyncmy
import xlsxwriter
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal

class ExcelExportWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, db_config, filename, company_name="WINESTORE", student_name=""):
        super().__init__()
        self.db_config = db_config
        self.filename = filename
        self.company_name = company_name
        self.student_name = student_name
        self.workbook = None
        self.styles = {}
    
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.export_to_excel())
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
            ORDER BY wb.Vintage DESC, wb.PurchasePrice DESC
            """
            
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                result = await cursor.fetchall()
            
            await conn.ensure_closed()
            return result
        except Exception as e:
            print(f"Ошибка при получении данных: {e}")
            return []
    
    async def fetch_analytics_data(self):
        """Получение данных для аналитики"""
        try:
            conn = await self.get_connection()
            
            queries = {
                'region_stats': """
                    SELECT Region, COUNT(*) as Count, AVG(PurchasePrice) as AvgPrice,
                           SUM(PurchasePrice) as TotalValue
                    FROM WineBottle 
                    WHERE Region IS NOT NULL AND Region != ''
                    GROUP BY Region 
                    ORDER BY Count DESC
                """,
                'vintage_stats': """
                    SELECT Vintage, COUNT(*) as Count, AVG(PurchasePrice) as AvgPrice
                    FROM WineBottle 
                    WHERE Vintage IS NOT NULL 
                    GROUP BY Vintage 
                    ORDER BY Vintage DESC
                """,
                'price_ranges': """
                    SELECT 
                        CASE 
                            WHEN PurchasePrice < 1000 THEN 'До 1000'
                            WHEN PurchasePrice BETWEEN 1000 AND 5000 THEN '1000-5000'
                            WHEN PurchasePrice BETWEEN 5000 AND 10000 THEN '5000-10000'
                            ELSE 'Свыше 10000'
                        END as PriceRange,
                        COUNT(*) as Count,
                        SUM(PurchasePrice) as TotalValue
                    FROM WineBottle 
                    WHERE PurchasePrice IS NOT NULL
                    GROUP BY PriceRange
                    ORDER BY TotalValue DESC
                """,
                'producer_stats': """
                    SELECT Producer, COUNT(*) as Count, AVG(PurchasePrice) as AvgPrice,
                           SUM(PurchasePrice) as TotalValue
                    FROM WineBottle 
                    WHERE Producer IS NOT NULL AND Producer != ''
                    GROUP BY Producer 
                    HAVING COUNT(*) > 0
                    ORDER BY Count DESC, AvgPrice DESC
                """
            }
            
            analytics_data = {}
            
            async with conn.cursor() as cursor:
                for key, query in queries.items():
                    await cursor.execute(query)
                    analytics_data[key] = await cursor.fetchall()
                    
            await conn.ensure_closed()
            return analytics_data
        except Exception as e:
            print(f"Ошибка при получении аналитики: {e}")
            return {}
    
    def create_styles(self):
        """Создание стилей для оформления отчета"""
        styles = {}
        
        # Заголовок отчета (14pt, жирный, цвет фона)
        styles['title'] = self.workbook.add_format({
            'bold': True,
            'font_size': 14,
            'font_color': '#FFFFFF',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'fg_color': '#366092'
        })
        
        # Подзаголовок
        styles['subtitle'] = self.workbook.add_format({
            'bold': True,
            'font_size': 12,
            'font_color': '#1F497D',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'fg_color': '#DCE6F1'
        })
        
        # Заголовки таблиц
        styles['header'] = self.workbook.add_format({
            'bold': True,
            'font_size': 11,
            'font_color': 'white',
            'bg_color': '#4472C4',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        
        # Основной текст
        styles['normal'] = self.workbook.add_format({
            'border': 1,
            'align': 'left',
            'valign': 'top'
        })
        
        # Числовые значения
        styles['number'] = self.workbook.add_format({
            'border': 1,
            'align': 'right',
            'num_format': '#,##0.00'
        })
        
        # Денежный формат
        styles['currency'] = self.workbook.add_format({
            'border': 1,
            'align': 'right',
            'num_format': '#,##0.00'
        })
        
        # Центрированный текст
        styles['center'] = self.workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'center'
        })
        
        return styles
    
    def create_data_sheet(self, wine_data):
        """Создание листа 'Данные проекта'"""
        data_sheet = self.workbook.add_worksheet('Данные проекта')
        
        # Заголовок отчета
        data_sheet.merge_range('A1:J1', f'{self.company_name} - УПРАВЛЕНИЕ ВИННОЙ КОЛЛЕКЦИЕЙ', self.styles['title'])
        
        if self.student_name:
            data_sheet.merge_range('A2:J2', f'Студент: {self.student_name}', self.styles['subtitle'])
        else:
            data_sheet.merge_range('A2:J2', '', self.styles['subtitle'])
            
        data_sheet.merge_range('A3:J3', f'Дата формирования отчета: {datetime.now().strftime("%d.%m.%Y %H:%M")}', self.styles['center'])
        
        # Заголовки таблицы
        headers = [
            'ID', 'Название вина', 'Производитель', 'Винтаж', 'Регион',
            'Цена покупки', 'Дата покупки', 'Полка', 'Стойка', 'Погреб'
        ]
        
        for col, header in enumerate(headers):
            data_sheet.write(4, col, header, self.styles['header'])
        
        # Данные таблицы
        for row, record in enumerate(wine_data, start=5):
            for col, value in enumerate(record):
                cell_style = self.styles['normal']
                
                # Определяем стиль в зависимости от типа данных
                if col == 5:  # PurchasePrice
                    cell_style = self.styles['currency']
                elif col in [0, 3]:  # BottleID, Vintage
                    cell_style = self.styles['number']
                elif col == 6:  # PurchaseDate
                    if value:
                        cell_style = self.styles['center']
                
                data_sheet.write(row, col, value, cell_style)
        
        # Автофильтры для всех колонок таблицы
        data_sheet.autofilter(4, 0, 4 + len(wine_data), len(headers) - 1)
        
        # Закрепленная область заголовков
        data_sheet.freeze_panes(5, 0)
        
        # Настроенная ширина столбцов
        column_widths = [8, 25, 20, 10, 15, 12, 12, 8, 8, 15]
        for col, width in enumerate(column_widths):
            data_sheet.set_column(col, col, width)
    
    def create_analytics_sheet(self, analytics_data, wine_data):
        """Создание листа 'Аналитика'"""
        analytics_sheet = self.workbook.add_worksheet('Аналитика')
        current_row = 0
        
        # Заголовок
        analytics_sheet.merge_range(current_row, 0, current_row, 6, 
                                  'АНАЛИТИКА ВИННОЙ КОЛЛЕКЦИИ', self.styles['title'])
        current_row += 1
        analytics_sheet.merge_range(current_row, 0, current_row, 6, 
                                  'Сводные данные и ключевые метрики', self.styles['subtitle'])
        current_row += 2
        
        if not analytics_data.get('region_stats'):
            analytics_sheet.write(current_row, 0, 'Нет данных для аналитики', self.styles['normal'])
            return
        
        # Сводная таблица с ключевыми метриками проекта
        analytics_sheet.write(current_row, 0, 'СВОДНАЯ ТАБЛИЦА ПО РЕГИОНАМ', self.styles['header'])
        current_row += 1
        
        headers = ['Регион', 'Кол-во бутылок', 'Средняя цена', 'Общая стоимость']
        for col, header in enumerate(headers):
            analytics_sheet.write(current_row, col, header, self.styles['header'])
        current_row += 1
        
        region_data = analytics_data['region_stats']
        total_collection_value = sum(float(record[3]) for record in region_data if record[3])
        
        for region, count, avg_price, total_value in region_data:
            analytics_sheet.write(current_row, 0, region, self.styles['normal'])
            analytics_sheet.write(current_row, 1, count, self.styles['number'])
            analytics_sheet.write(current_row, 2, float(avg_price) if avg_price else 0, self.styles['currency'])
            analytics_sheet.write(current_row, 3, float(total_value) if total_value else 0, self.styles['currency'])
            current_row += 1
        
        current_row += 2
        
        # Статистика по ценовым диапазонам
        analytics_sheet.write(current_row, 0, 'СТАТИСТИКА ПО ЦЕНОВЫМ ДИАПАЗОНАМ', self.styles['header'])
        current_row += 1
        
        headers = ['Ценовой диапазон', 'Кол-во бутылок', 'Общая стоимость']
        for col, header in enumerate(headers):
            analytics_sheet.write(current_row, col, header, self.styles['header'])
        current_row += 1
        
        price_data = analytics_data['price_ranges']
        for price_range, count, total_val in price_data:
            analytics_sheet.write(current_row, 0, price_range, self.styles['normal'])
            analytics_sheet.write(current_row, 1, count, self.styles['number'])
            analytics_sheet.write(current_row, 2, float(total_val) if total_val else 0, self.styles['currency'])
            current_row += 1
        
        current_row += 2
        
        # Блок с расчетными показателями
        analytics_sheet.write(current_row, 0, 'РАСЧЕТНЫЕ ПОКАЗАТЕЛИ', self.styles['header'])
        current_row += 1
        
        total_bottles = len(wine_data)
        total_value = sum(float(record[5]) for record in wine_data if record[5] is not None)
        avg_bottle_price = total_value / total_bottles if total_bottles > 0 else 0
        
        if wine_data:
            prices = [float(record[5]) for record in wine_data if record[5] is not None]
            max_price = max(prices) if prices else 0
            min_price = min(prices) if prices else 0
        else:
            max_price = 0
            min_price = 0
        
        indicators = [
            ('Общее количество бутылок:', total_bottles, self.styles['number']),
            ('Общая стоимость коллекции:', total_value, self.styles['currency']),
            ('Средняя стоимость бутылки:', avg_bottle_price, self.styles['currency']),
            ('Самая дорогая бутылка:', max_price, self.styles['currency']),
            ('Самая доступная бутылка:', min_price, self.styles['currency']),
            ('Разброс цен:', max_price - min_price, self.styles['currency'])
        ]
        
        for indicator, value, style in indicators:
            analytics_sheet.write(current_row, 0, indicator, self.styles['normal'])
            analytics_sheet.write(current_row, 1, value, style)
            current_row += 1
        
        current_row += 2
        
        # Выводы по аналитике
        analytics_sheet.write(current_row, 0, 'ВЫВОДЫ ПО АНАЛИТИКЕ', self.styles['header'])
        current_row += 1
        
        top_regions = [region[0] for region in region_data[:3]] if region_data else ["нет данных"]
        top_prices = [price[0] for price in price_data[:2]] if price_data else ["нет данных"]
        
        conclusions = [
            f"• Коллекция состоит из {total_bottles} бутылок общей стоимостью {total_value:,.2f} руб.",
            f"• Средняя стоимость бутылки составляет {avg_bottle_price:.2f} руб.",
            f"• Наиболее представленные регионы: {', '.join(top_regions)}",
            f"• Преобладают вина в ценовом диапазоне: {', '.join(top_prices)}",
            f"• Разброс цен в коллекции: от {min_price:.2f} до {max_price:.2f} руб.",
            "• Коллекция демонстрирует разнообразие по регионам и ценовым категориям"
        ]
        
        for conclusion in conclusions:
            analytics_sheet.merge_range(current_row, 0, current_row, 4, conclusion, self.styles['normal'])
            current_row += 1
        
        # Создание диаграмм (минимум 2 разных типа)
        self.create_analytics_charts(analytics_sheet, analytics_data, len(region_data))
        
        # Настройка ширины колонок
        analytics_sheet.set_column('A:A', 20)
        analytics_sheet.set_column('B:B', 15)
        analytics_sheet.set_column('C:D', 15)
    
    def create_analytics_charts(self, sheet, analytics_data, region_count):
        """Создание диаграмм для аналитики"""
        if region_count == 0:
            return
            
        # Диаграмма 1: Столбчатая диаграмма - для сравнения категорий (по регионам)
        chart1 = self.workbook.add_chart({'type': 'column'})
        
        chart1.add_series({
            'name': 'Количество бутылок',
            'categories': f'=Аналитика!$A$6:$A${5 + region_count}',
            'values': f'=Аналитика!$B$6:$B${5 + region_count}',
        })
        
        chart1.set_title({'name': 'Распределение вин по регионам'})
        chart1.set_x_axis({'name': 'Регион'})
        chart1.set_y_axis({'name': 'Количество бутылок'})
        chart1.set_style(11)
        
        sheet.insert_chart('F2', chart1)
        
        # Диаграмма 2: Круговая диаграмма - для отображения долей (ценовые диапазоны)
        chart2 = self.workbook.add_chart({'type': 'pie'})
        
        price_data = analytics_data['price_ranges']
        if price_data:
            chart2.add_series({
                'name': 'Доли по ценовым диапазонам',
                'categories': f'=Аналитика!$A${13 + region_count}:$A${12 + region_count + len(price_data)}',
                'values': f'=Аналитика!$C${13 + region_count}:$C${12 + region_count + len(price_data)}',
                'data_labels': {'percentage': True, 'category': True}
            })
            
            chart2.set_title({'name': 'Распределение по ценовым диапазонам'})
            chart2.set_style(10)
            
            sheet.insert_chart('F18', chart2)
    
    def create_visualization_sheet(self, wine_data, analytics_data):
        """Создание листа 'Визуализация'"""
        visualization_sheet = self.workbook.add_worksheet('Визуализация')
        current_row = 0
        
        # Заголовок
        visualization_sheet.merge_range(current_row, 0, current_row, 6, 
                                     'ВИЗУАЛИЗАЦИЯ ДАННЫХ КОЛЛЕКЦИИ', self.styles['title'])
        current_row += 1
        visualization_sheet.merge_range(current_row, 0, current_row, 6, 
                                     'Графики и инфографика основных показателей', self.styles['subtitle'])
        current_row += 2
        
        if not wine_data:
            visualization_sheet.write(current_row, 0, 'Нет данных для визуализации', self.styles['normal'])
            return
        
        # Инфографика основных показателей
        total_bottles = len(wine_data)
        total_value = sum(float(record[5]) for record in wine_data if record[5] is not None)
        avg_price = total_value / total_bottles if total_bottles > 0 else 0
        
        # Блок с ключевыми метриками
        visualization_sheet.write(current_row, 0, 'ОСНОВНЫЕ ПОКАЗАТЕЛИ КОЛЛЕКЦИИ', self.styles['header'])
        current_row += 1
        
        metrics = [
            ('Общее количество бутылок', total_bottles, 'шт.'),
            ('Общая стоимость коллекции', f"{total_value:,.2f}", 'руб.'),
            ('Средняя стоимость бутылки', f"{avg_price:.2f}", 'руб.'),
            ('Количество производителей', len(set(record[2] for record in wine_data if record[2])), ''),
            ('Количество регионов', len(set(record[4] for record in wine_data if record[4])), '')
        ]
        
        for i, (metric_name, value, unit) in enumerate(metrics):
            visualization_sheet.write(current_row + i, 0, metric_name, self.styles['header'])
            visualization_sheet.write(current_row + i, 1, value, self.styles['number'])
            visualization_sheet.write(current_row + i, 2, unit, self.styles['normal'])
        
        current_row += len(metrics) + 2
        
        # Дополнительные графики
        self.create_visualization_charts(visualization_sheet, analytics_data, current_row)
        
        # Настройка ширины колонок
        visualization_sheet.set_column('A:A', 25)
        visualization_sheet.set_column('B:B', 15)
        visualization_sheet.set_column('C:C', 8)
    
    def create_visualization_charts(self, sheet, analytics_data, start_row):
        """Создание дополнительных графиков для визуализации"""
        # График 1: Линейный график - для трендов во времени (по винтажам)
        vintage_data = analytics_data.get('vintage_stats', [])
        if vintage_data:
            data_start_row = start_row + 2
            sheet.write(data_start_row - 1, 0, 'Винтаж', self.styles['header'])
            sheet.write(data_start_row - 1, 1, 'Средняя цена', self.styles['header'])
            sheet.write(data_start_row - 1, 2, 'Количество', self.styles['header'])
            
            for i, (vintage, count, avg_price) in enumerate(vintage_data):
                sheet.write(data_start_row + i, 0, vintage, self.styles['number'])
                sheet.write(data_start_row + i, 1, float(avg_price) if avg_price else 0, self.styles['currency'])
                sheet.write(data_start_row + i, 2, count, self.styles['number'])
            
            # Линейный график
            chart1 = self.workbook.add_chart({'type': 'line'})
            
            chart1.add_series({
                'name': 'Средняя цена по винтажам',
                'categories': f'=Визуализация!$A${data_start_row + 1}:$A${data_start_row + len(vintage_data)}',
                'values': f'=Визуализация!$B${data_start_row + 1}:$B${data_start_row + len(vintage_data)}',
                'marker': {'type': 'circle', 'size': 6},
            })
            
            chart1.set_title({'name': 'Динамика средней цены по винтажам'})
            chart1.set_x_axis({'name': 'Винтаж'})
            chart1.set_y_axis({'name': 'Средняя цена'})
            chart1.set_style(10)
            
            sheet.insert_chart('E2', chart1)
    
    async def export_to_excel(self):
        """Основной метод экспорта данных в Excel"""
        print("Начало экспорта данных в Excel...")
        
        # Получение данных из БД
        wine_data = await self.fetch_wine_data()
        analytics_data = await self.fetch_analytics_data()
        
        print(f"Получено {len(wine_data)} записей о винах")
        
        # Создание Excel файла
        self.workbook = xlsxwriter.Workbook(self.filename)
        self.styles = self.create_styles()
        
        # Создание листов
        self.create_data_sheet(wine_data)
        self.create_analytics_sheet(analytics_data, wine_data)
        self.create_visualization_sheet(wine_data, analytics_data)
        
        # Закрытие workbook
        self.workbook.close()
        print(f"Экспорт в Excel завершен! Файл сохранен как: {self.filename}")
        
        return self.filename
