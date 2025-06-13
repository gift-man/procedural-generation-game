"""Менеджер провинций."""
from typing import Dict, Set, Tuple, Optional
from dataclasses import dataclass
from collections import deque

@dataclass
class ProvinceConfig:
    """Конфигурация провинций."""
    min_size: int = 4
    max_size: int = 8
    min_provinces: int = 5
    max_provinces: int = 7

class ProvinceManager:
    """Класс для управления провинциями."""
    
    def __init__(self):
        """Инициализация менеджера."""
        self.provinces: Dict[int, Set[Tuple[int, int]]] = {}  # id -> клетки
        self.next_id: int = 0
        self.config = ProvinceConfig()
        self.cell_to_province: Dict[Tuple[int, int], int] = {}  # клетка -> id провинции
    
    def create_province(self) -> int:
        """Создает новую провинцию."""
        province_id = self.next_id
        self.next_id += 1
        self.provinces[province_id] = set()
        return province_id
    
    def add_cell_to_province(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """
        Добавляет клетку в провинцию.
        
        Args:
            province_id: ID провинции
            cell: Координаты клетки
            
        Returns:
            bool: True если клетка добавлена успешно
        """
        if province_id not in self.provinces:
            return False
            
        if cell in self.cell_to_province:
            return False
            
        province = self.provinces[province_id]
        
        # Проверяем размер
        if len(province) >= self.config.max_size:
            return False
            
        # Проверяем связность
        if province and not self._is_adjacent(cell, province):
            return False
            
        # Проверяем плюсовые пересечения
        if not self._check_plus_intersection(cell, province):
            return False
            
        province.add(cell)
        self.cell_to_province[cell] = province_id
        return True
    
    def get_provinces(self) -> Dict[int, Set[Tuple[int, int]]]:
        """Возвращает все провинции."""
        return self.provinces
    
    def _is_adjacent(self, cell: Tuple[int, int], 
                    province: Set[Tuple[int, int]]) -> bool:
        """Проверяет, прилегает ли клетка к провинции."""
        x, y = cell
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if (x + dx, y + dy) in province:
                return True
        return False
    
    def _check_plus_intersection(self, cell: Tuple[int, int], 
                               province: Set[Tuple[int, int]]) -> bool:
        """
        Проверяет, не образует ли добавление клетки плюсовое пересечение.
        """
        x, y = cell
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        # Проверяем количество занятых направлений
        occupied = sum(1 for dx, dy in directions 
                      if (x + dx, y + dy) in province or
                         (x + dx, y + dy) in self.cell_to_province)
                         
        return occupied < 4  # Плюсовое пересечение = 4 соседа
    
    def verify_province(self, province_id: int) -> bool:
        """Проверяет корректность провинции."""
        if province_id not in self.provinces:
            return False
            
        province = self.provinces[province_id]
        
        # Проверка размера
        if not (self.config.min_size <= len(province) <= self.config.max_size):
            return False
            
        # Проверка связности
        if not self._verify_connectivity(province):
            return False
            
        return True
    
    def _verify_connectivity(self, cells: Set[Tuple[int, int]]) -> bool:
        """Проверяет связность клеток."""
        if not cells:
            return True
            
        start = next(iter(cells))
        visited = {start}
        queue = deque([start])
        
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor in cells and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        return len(visited) == len(cells)