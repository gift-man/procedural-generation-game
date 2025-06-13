"""Компонент провинции."""
from typing import Set, List, Tuple, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class Province:
    """Класс, представляющий провинцию на карте."""
    
    def __init__(self, id: int, center_x: int, center_y: int):
        """
        Инициализация провинции.
        
        Args:
            id (int): Уникальный идентификатор провинции
            center_x (int): X координата центра провинции
            center_y (int): Y координата центра провинции
        """
        self.id = id
        self.center_x = center_x
        self.center_y = center_y
        self.cells: Set[Tuple[int, int]] = set()  # Множество клеток провинции
        self.border_cells: Set[Tuple[int, int]] = set()  # Множество граничных клеток
        self.neighbors: Set[int] = set()  # Множество соседних провинций
        
        # Случайный цвет для провинции (исключая слишком темные и светлые оттенки)
        import random
        self.color = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )
        
    def update_border_cells(self) -> None:
        """Обновляет список граничных клеток."""
        self.border_cells = {
            (x, y) for x, y in self.cells
            if any((x + dx, y + dy) not in self.cells
                  for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)])
        }
    
    def add_cell(self, cell: Tuple[int, int]) -> None:
        """Добавляет клетку в провинцию."""
        self.cells.add(cell)
        self.update_border_cells()
        
    def remove_cell(self, cell: Tuple[int, int]) -> None:
        """Удаляет клетку из провинции."""
        self.cells.discard(cell)
        self.update_border_cells()

    def is_adjacent(self, cell: Tuple[int, int]) -> bool:
        """Проверяет, прилегает ли клетка к провинции."""
        x, y = cell
        return any((x + dx, y + dy) in self.cells
                  for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)])