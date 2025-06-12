"""Анализатор островов."""
from typing import Set, Tuple, Dict, List
from dataclasses import dataclass
import math
from collections import deque

@dataclass
class IslandAnalysis:
    """Результаты анализа острова."""
    total_cells: int
    width: int
    height: int
    center: Tuple[float, float]
    narrowest_width: int
    recommended_provinces: int
    recommended_sizes: Dict[int, float]  # размер: доля провинций этого размера

class IslandAnalyzer:
    """Анализатор структуры острова."""
    
    def analyze_island(self, cells: Set[Tuple[int, int]]) -> IslandAnalysis:
        """Анализирует остров и возвращает рекомендации по генерации провинций."""
        if not cells:
            raise ValueError("Empty island")
            
        # Базовые метрики
        x_coords = [x for x, _ in cells]
        y_coords = [y for _, y in cells]
        width = max(x_coords) - min(x_coords) + 1
        height = max(y_coords) - min(y_coords) + 1
        center_x = sum(x_coords) / len(cells)
        center_y = sum(y_coords) / len(cells)
        
        # Находим самые узкие места
        narrowest = self._find_narrowest_width(cells)
        
        # Рассчитываем рекомендуемое количество провинций
        total_cells = len(cells)
        recommended_provinces = self._calculate_recommended_provinces(total_cells, narrowest)
        
        # Рассчитываем рекомендуемые размеры провинций
        sizes = self._calculate_size_distribution(total_cells, recommended_provinces)
        
        return IslandAnalysis(
            total_cells=total_cells,
            width=width,
            height=height,
            center=(center_x, center_y),
            narrowest_width=narrowest,
            recommended_provinces=recommended_provinces,
            recommended_sizes=sizes
        )
    
    def _find_narrowest_width(self, cells: Set[Tuple[int, int]]) -> int:
        """Находит минимальную ширину острова."""
        narrowest = float('inf')
        
        # Для каждой строки находим максимальную непрерывную последовательность
        x_coords = set(x for x, _ in cells)
        y_coords = set(y for _, y in cells)
        
        for y in range(min(y_coords), max(y_coords) + 1):
            # Находим все x-координаты в текущей строке
            row_cells = [x for x in x_coords if (x, y) in cells]
            if not row_cells:
                continue
                
            # Ищем разрывы
            row_cells.sort()
            current_width = 1
            max_width_in_row = 1
            
            for i in range(1, len(row_cells)):
                if row_cells[i] - row_cells[i-1] == 1:
                    current_width += 1
                else:
                    max_width_in_row = max(max_width_in_row, current_width)
                    current_width = 1
                    
            max_width_in_row = max(max_width_in_row, current_width)
            if max_width_in_row > 0:
                narrowest = min(narrowest, max_width_in_row)
        
        return narrowest if narrowest != float('inf') else 1
    
    def _calculate_recommended_provinces(self, total_cells: int, narrowest: int) -> int:
        """Рассчитывает рекомендуемое количество провинций."""
        # Базовый расчет: 1 провинция на каждые 6 клеток
        base_count = total_cells // 6
        
        # Корректируем с учетом узких мест
        if narrowest < 4:
            # Для очень узких островов уменьшаем количество провинций
            base_count = max(3, base_count - 2)
        elif narrowest < 6:
            # Для средних островов немного уменьшаем
            base_count = max(3, base_count - 1)
            
        # Ограничиваем минимальным и максимальным значением
        return max(3, min(base_count, total_cells // 4))
    
    def _calculate_size_distribution(self, total_cells: int, 
                                  num_provinces: int) -> Dict[int, float]:
        """Рассчитывает распределение размеров провинций."""
        avg_size = total_cells / num_provinces
        
        # Определяем возможные размеры провинций
        if avg_size <= 5:
            return {4: 0.7, 5: 0.3}
        elif avg_size <= 6:
            return {4: 0.3, 5: 0.4, 6: 0.3}
        elif avg_size <= 7:
            return {5: 0.3, 6: 0.4, 7: 0.3}
        else:
            return {6: 0.4, 7: 0.4, 8: 0.2}