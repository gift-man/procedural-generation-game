"""Компонент провинции."""
import random
from typing import Set, List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from ..world.generators.province_settings import ProvinceGenerationConfig

@dataclass
class Province:
    """Базовый класс провинции."""
    id: int
    cells: Set[Tuple[int, int]]

@dataclass
class ProvinceData:
    """Класс для хранения данных о провинции."""
    cells: Set[Tuple[int, int]] = field(default_factory=set)  # Клетки провинции
    neighbors: Set[int] = field(default_factory=set)          # ID соседних провинций
    border_cells: Set[Tuple[int, int]] = field(default_factory=set)  # Граничные клетки
    target_size: Optional[int] = None  # Целевой размер провинции
    
    # Метрики для анализа качества
    center: Optional[Tuple[int, int]] = None  # Центр провинции
    compactness: float = 0.0  # Показатель компактности формы
    border_length: int = 0    # Длина границы провинции
    
    def update_metrics(self) -> None:
        """Обновляет метрики провинции."""
        if not self.cells:
            return
            
        # Вычисляем центр
        x_sum = sum(x for x, _ in self.cells)
        y_sum = sum(y for _, y in self.cells)
        self.center = (x_sum // len(self.cells), y_sum // len(self.cells))
        
        # Вычисляем компактность
        max_distance = 0
        for cell in self.cells:
            dx = cell[0] - self.center[0]
            dy = cell[1] - self.center[1]
            distance = dx * dx + dy * dy
            max_distance = max(max_distance, distance)
        self.compactness = len(self.cells) / (max_distance + 1)
        
        # Вычисляем длину границы
        self.border_length = sum(
            1 for x, y in self.cells
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
            if (x + dx, y + dy) not in self.cells
        )
        
        # Обновляем граничные клетки
        self.border_cells = {
            (x, y) for x, y in self.cells
            if any((x + dx, y + dy) not in self.cells
                  for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)])
        }