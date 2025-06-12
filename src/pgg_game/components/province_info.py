"""Компонент информации о провинции."""
from typing import Set, Tuple, Optional

class ProvinceInfoComponent:
    """Хранит информацию о провинции."""
    
    def __init__(self, name: str, min_size: int = 4):
        """
        Инициализация компонента.
        
        Args:
            name: Название провинции
            min_size: Минимальный размер провинции
        """
        self.name = name
        self.min_size = min_size
        self.cells: Set[Tuple[int, int]] = set()
        self.owner: Optional[int] = None
        self.population = 0
        self.defense = 1
        self.income = 0
        self.has_town_hall = False
        self.town_hall_position: Optional[Tuple[int, int]] = None
        self.neighbors: Set[int] = set()
    
    def add_cells(self, cells: Set[Tuple[int, int]]) -> None:
        """Добавляет клетки в провинцию."""
        if len(cells) < self.min_size:
            raise ValueError(f"Провинция должна содержать минимум {self.min_size} клеток")
        self.cells = cells.copy()