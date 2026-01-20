from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Wine:
    """Класс для представления вина"""
    bottle_id: int
    varietal: str
    producer: str
    vintage_year: int
    region: str
    price: float
    purchase_date: Optional[datetime] = None
    shelf: str = ""
    rack: str = ""
    cellar: str = ""
    status: str = "in_storage"
    serial_number: str = ""
    volume: int = 750
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'BottleID': self.bottle_id,
            'Varietal': self.varietal,
            'Producer': self.producer,
            'VintageYear': self.vintage_year,
            'Region': self.region,
            'Price': self.price,
            'PurchaseDate': self.purchase_date,
            'Shelf': self.shelf,
            'Rack': self.rack,
            'Cellar': self.cellar,
            'Status': self.status,
            'SerialNumber': self.serial_number,
            'Volume': self.volume
        }
    
    @classmethod
    def from_db_row(cls, row):
        """Создание объекта из строки базы данных"""
        return cls(
            bottle_id=row[0],
            varietal=row[1] or '',
            producer=row[2] or '',
            vintage_year=row[3] or 0,
            region=row[4] or '',
            price=float(row[5]) if row[5] else 0.0,
            purchase_date=row[6],
            shelf=row[7] or '',
            rack=row[8] or '',
            cellar=row[9] or ''
        )

@dataclass
class WineLocation:
    """Класс для представления местоположения вина"""
    bottle_id: int
    shelf: str = ""
    rack: str = ""
    cellar: str = ""
    quantity: int = 1
    
    def to_dict(self):
        """Преобразование в словарь"""
        return {
            'BottleID': self.bottle_id,
            'Shelf': self.shelf,
            'Rack': self.rack,
            'Cellar': self.cellar,
            'Quantity': self.quantity
        }
