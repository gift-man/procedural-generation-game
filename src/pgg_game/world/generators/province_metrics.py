"""Метрики для оценки качества провинций."""
import math
from typing import Set, Tuple, Dict, List
from collections import deque
from dataclasses import dataclass

@dataclass
class ProvinceMetrics:
    """Метрики качества провинции."""
    compactness: float = 0.0   # Насколько компактна форма
    connectivity: float = 0.0   # Насколько хорошо соединены клетки
    balance: float = 0.0       # Насколько сбалансирован размер
    border_length: int = 0     # Длина границы
    center: Tuple[float, float] = (0.0, 0.0)  # Центр масс

class ProvinceAnalyzer:
    """Анализатор качества провинций."""
    
    @staticmethod
    def calculate_metrics(cells: Set[Tuple[int, int]]) -> ProvinceMetrics:
        """Вычисляет метрики качества для провинции."""
        if not cells:
            return ProvinceMetrics()
            
        metrics = ProvinceMetrics()
        
        # Вычисляем центр масс
        sum_x = sum(x for x, _ in cells)
        sum_y = sum(y for _, y in cells)
        count = len(cells)
        center_x = sum_x / count
        center_y = sum_y / count
        metrics.center = (center_x, center_y)
        
        # Вычисляем компактность
        max_distance = 0
        sum_distance = 0
        for x, y in cells:
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            max_distance = max(max_distance, distance)
            sum_distance += distance
        
        ideal_radius = math.sqrt(count / math.pi)
        metrics.compactness = ideal_radius / (sum_distance / count) if sum_distance > 0 else 1.0
        
        # Вычисляем связность
        metrics.connectivity = ProvinceAnalyzer._calculate_connectivity(cells)
        
        # Вычисляем длину границы
        metrics.border_length = ProvinceAnalyzer._calculate_border_length(cells)
        
        return metrics
    
    @staticmethod
    def _calculate_connectivity(cells: Set[Tuple[int, int]]) -> float:
        """Вычисляет метрику связности провинции."""
        if not cells:
            return 0.0
            
        # Начинаем с первой клетки
        start = next(iter(cells))
        visited = {start}
        queue = deque([start])
        
        # Обход в ширину
        while queue:
            current = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in cells and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        # Возвращаем долю достижимых клеток
        return len(visited) / len(cells)
    
    @staticmethod
    def _calculate_border_length(cells: Set[Tuple[int, int]]) -> int:
        """Вычисляет длину границы провинции."""
        border_length = 0
        for x, y in cells:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                if (x + dx, y + dy) not in cells:
                    border_length += 1
        return border_length