"""Компонент информации о провинции."""
from typing import Set, Tuple, Optional

class ProvinceInfoComponent:
    """Хранит информацию о провинции."""
    
    def __init__(self, name: str):
        """
        Инициализация компонента.
        
        Args:
            name: Название провинции
        """
        self.name = name
        self.cells: Set[Tuple[int, int]] = set()  # Множество клеток провинции
        self.owner: Optional[int] = None  # ID игрока-владельца
        self.population = 0
        self.defense = 1
        self.income = 0
        self.has_town_hall = False
        self.town_hall_position: Optional[Tuple[int, int]] = None
        self.neighbors: Set[int] = set()  # ID соседних провинций
    
    def add_neighbor(self, province_id: int) -> None:
        """Добавляет соседнюю провинцию."""
        self.neighbors.add(province_id)