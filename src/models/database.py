import asyncio
import asyncmy
from PyQt6.QtCore import QThread, pyqtSignal
from datetime import datetime

class DatabaseWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, coroutine, *args, **kwargs):
        super().__init__()
        self.coroutine = coroutine
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.coroutine(*self.args, **self.kwargs))
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class AsyncDatabaseManager:
    def __init__(self):
        self.connection_params = {
            'host': 'localhost',
            'user': 'maksim',
            'password': '12345',
            'db': 'is21-18',
            'charset': 'utf8mb4'
        }

    async def _get_connection(self):
        """Создание нового соединения"""
        try:
            return await asyncmy.connect(**self.connection_params)
        except Exception as e:
            print(f"Ошибка подключения к базе данных: {e}")
            return None

    async def execute_query(self, query, params=None):
        """Асинхронное выполнение SQL запроса"""
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                return None
                
            async with conn.cursor() as cursor:
                await cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    result = await cursor.fetchall()
                    return result
                else:
                    await conn.commit()
                    return cursor.rowcount
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            print(f"Запрос: {query}")
            print(f"Параметры: {params}")
            return None
        finally:
            if conn:
                await conn.ensure_closed()

    async def get_wine_bottles(self):
        """Асинхронное получение всех записей о винах"""
        query = """
        SELECT wb.BottleID, wb.WineName, wb.Producer, wb.Vintage, 
               wb.Region, wb.PurchasePrice, wb.PurchaseDate,
               wl.Shelf, wl.Rack, wl.Cellar
        FROM WineBottle wb
        LEFT JOIN WineLocation wl ON wb.BottleID = wl.BottleID
        ORDER BY wb.BottleID DESC
        """
        result = await self.execute_query(query)
        if result:
            wines = []
            for row in result:
                wine_data = {
                    'BottleID': row[0],
                    'Varietal': row[1] or '',
                    'Producer': row[2] or '',
                    'VintageYear': row[3] or '',
                    'Region': row[4] or '',
                    'Price': float(row[5]) if row[5] else 0.0,
                    'PurchaseDate': row[6],
                    'Shelf': row[7] or '',
                    'Rack': row[8] or '',
                    'Cellar': row[9] or '',
                    'Status': 'in_storage',
                    'SerialNumber': str(row[0]),
                    'Volume': 750
                }
                wines.append(wine_data)
            return wines
        return []

    async def add_wine_bottle(self, data):
        """Асинхронное добавление новой записи о вине"""
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                return False

            async with conn.cursor() as cursor:
                # Вставка основной записи о вине
                query = """
                INSERT INTO WineBottle 
                (WineName, Producer, Vintage, Region, PurchasePrice, PurchaseDate)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                # Обработка даты - если пустая строка, устанавливаем None
                purchase_date = data.get('purchase_date')
                if purchase_date == '':
                    purchase_date = None
                
                # Ограничение цены до 999999.99
                price = min(float(data.get('price', 0)), 999999.99)
                
                params = (
                    data.get('name', ''),
                    data.get('producer', ''),
                    data.get('vintage_year', ''),
                    data.get('region', ''),
                    price,
                    purchase_date
                )
                
                await cursor.execute(query, params)
                
                # Получаем ID новой записи
                await cursor.execute("SELECT LAST_INSERT_ID()")
                id_result = await cursor.fetchone()
                if id_result:
                    new_id = id_result[0]
                    
                    # Добавляем запись о местоположении если указано
                    if any([data.get('shelf'), data.get('rack'), data.get('cellar')]):
                        loc_query = """
                        INSERT INTO WineLocation (Shelf, Rack, Cellar, BottleID, Quantity)
                        VALUES (%s, %s, %s, %s, 1)
                        """
                        loc_params = (
                            data.get('shelf', ''),
                            data.get('rack', ''), 
                            data.get('cellar', ''),
                            new_id
                        )
                        await cursor.execute(loc_query, loc_params)
                    
                    await conn.commit()
                    return True
            return False
        except Exception as e:
            print(f"Ошибка добавления вина: {e}")
            if conn:
                await conn.rollback()
            return False
        finally:
            if conn:
                await conn.ensure_closed()

    async def update_wine_bottle(self, bottle_id, data):
        """Асинхронное обновление записи о вине"""
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                return False

            async with conn.cursor() as cursor:
                query = """
                UPDATE WineBottle 
                SET WineName=%s, Producer=%s, Vintage=%s, Region=%s, 
                    PurchasePrice=%s, PurchaseDate=%s
                WHERE BottleID=%s
                """
                
                # Обработка даты - если пустая строка, устанавливаем None
                purchase_date = data.get('PurchaseDate')
                if purchase_date == '':
                    purchase_date = None
                
                # Ограничение цены
                price = min(float(data.get('Price', 0)), 999999.99)
                
                params = (
                    data.get('Varietal', ''),
                    data.get('Producer', ''),
                    data.get('VintageYear', ''),
                    data.get('Region', ''),
                    price,
                    purchase_date,
                    bottle_id
                )
                
                await cursor.execute(query, params)
                
                # Обновляем местоположение
                # Удаляем старую запись о местоположении
                await cursor.execute("DELETE FROM WineLocation WHERE BottleID=%s", (bottle_id,))
                
                # Создаем новую запись если указано местоположение
                if any([data.get('Shelf'), data.get('Rack'), data.get('Cellar')]):
                    insert_loc_query = """
                    INSERT INTO WineLocation (Shelf, Rack, Cellar, BottleID, Quantity)
                    VALUES (%s, %s, %s, %s, 1)
                    """
                    insert_loc_params = (
                        data.get('Shelf', ''),
                        data.get('Rack', ''), 
                        data.get('Cellar', ''),
                        bottle_id
                    )
                    await cursor.execute(insert_loc_query, insert_loc_params)
                
                await conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка обновления вина: {e}")
            if conn:
                await conn.rollback()
            return False
        finally:
            if conn:
                await conn.ensure_closed()

    async def delete_wine_bottle(self, bottle_id):
        """Асинхронное удаление записи о вине"""
        conn = None
        try:
            conn = await self._get_connection()
            if not conn:
                return False

            async with conn.cursor() as cursor:
                # Сначала удаляем связанные записи о местоположении
                await cursor.execute("DELETE FROM WineLocation WHERE BottleID=%s", (bottle_id,))
                # Затем удаляем саму запись о вине
                await cursor.execute("DELETE FROM WineBottle WHERE BottleID=%s", (bottle_id,))
                await conn.commit()
                return True
        except Exception as e:
            print(f"Ошибка удаления вина: {e}")
            if conn:
                await conn.rollback()
            return False
        finally:
            if conn:
                await conn.ensure_closed()

    async def search_wines(self, search_term="", filters=None):
        """Асинхронный поиск вин с фильтрацией"""
        try:
            base_query = """
            SELECT wb.BottleID, wb.WineName, wb.Producer, wb.Vintage, 
                   wb.Region, wb.PurchasePrice, wb.PurchaseDate,
                   wl.Shelf, wl.Rack, wl.Cellar
            FROM WineBottle wb
            LEFT JOIN WineLocation wl ON wb.BottleID = wl.BottleID
            WHERE 1=1
            """
            params = []
            
            if search_term:
                base_query += " AND (wb.WineName LIKE %s OR wb.Producer LIKE %s OR wb.Region LIKE %s)"
                params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
            
            if filters:
                if filters.get('region'):
                    base_query += " AND wb.Region = %s"
                    params.append(filters['region'])
                if filters.get('min_year'):
                    base_query += " AND wb.Vintage >= %s"
                    params.append(filters['min_year'])
                if filters.get('max_year'):
                    base_query += " AND wb.Vintage <= %s"
                    params.append(filters['max_year'])
            
            base_query += " ORDER BY wb.BottleID DESC"
            
            result = await self.execute_query(base_query, params)
            if result:
                wines = []
                for row in result:
                    wine_data = {
                        'BottleID': row[0],
                        'Varietal': row[1] or '',
                        'Producer': row[2] or '',
                        'VintageYear': row[3] or '',
                        'Region': row[4] or '',
                        'Price': float(row[5]) if row[5] else 0.0,
                        'PurchaseDate': row[6],
                        'Shelf': row[7] or '',
                        'Rack': row[8] or '',
                        'Cellar': row[9] or '',
                        'Status': 'in_storage',
                        'SerialNumber': str(row[0]),
                        'Volume': 750
                    }
                    wines.append(wine_data)
                return wines
            return []
        except Exception as e:
            print(f"Ошибка поиска вин: {e}")
            return []

    async def get_statistics(self):
        """Асинхронное получение статистики для графиков"""
        try:
            # Общая статистика
            total_query = "SELECT COUNT(*) FROM WineBottle"
            value_query = "SELECT SUM(PurchasePrice) FROM WineBottle"
            
            total_result = await self.execute_query(total_query)
            value_result = await self.execute_query(value_query)
            
            total_bottles = total_result[0][0] if total_result and total_result[0][0] else 0
            total_value = float(value_result[0][0]) if value_result and value_result[0][0] else 0.0
            
            # Статистика по регионам
            region_query = "SELECT Region, COUNT(*) FROM WineBottle WHERE Region IS NOT NULL AND Region != '' GROUP BY Region"
            region_data = await self.execute_query(region_query)
            regions = {}
            if region_data:
                for row in region_data:
                    if row[0]:  # Проверяем что регион не None и не пустой
                        regions[row[0]] = row[1]
            
            # Статистика по годам
            year_query = "SELECT Vintage, COUNT(*) FROM WineBottle WHERE Vintage IS NOT NULL GROUP BY Vintage ORDER BY Vintage"
            year_data = await self.execute_query(year_query)
            
            line_data = {'labels': [], 'values': []}
            if year_data:
                for row in year_data:
                    if row[0]:  # Проверяем что год не None
                        line_data['labels'].append(str(row[0]))
                        line_data['values'].append(row[1])
            
            pie_data = {
                'labels': list(regions.keys()),
                'values': list(regions.values())
            }
            
            return {
                'total_bottles': total_bottles,
                'in_storage': total_bottles,
                'consumed': 0,
                'total_value': total_value,
                'regions': regions,
                'line_data': line_data,
                'pie_data': pie_data
            }
        except Exception as e:
            print(f"Ошибка получения статистики: {e}")
            return {
                'total_bottles': 0,
                'in_storage': 0,
                'consumed': 0,
                'total_value': 0,
                'regions': {},
                'line_data': {'labels': [], 'values': []},
                'pie_data': {'labels': [], 'values': []}
            }
