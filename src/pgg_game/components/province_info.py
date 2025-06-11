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
        self.cells: Set[Tuple[int, int]] = set()
        self.owner: Optional[int] = None  # ID игрока-владельца
        self.population = 0
        self.defense = 1
        self.income = 0