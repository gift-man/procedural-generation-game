"""Генератор провинций."""
import random
import math
from typing import Set, Dict, List, Tuple, Optional
from collections import deque

from .province_settings import ProvinceGenerationConfig
from .province_metrics import ProvinceAnalyzer, ProvinceMetrics
from ...components.province import Province, ProvinceData
from ...config import GRID_WIDTH, GRID_HEIGHT

class ProvinceGenerator:
    """Улучшенный генератор провинций."""
    
    def __init__(self, config: Optional[ProvinceGenerationConfig] = None):
        """Инициализация генератора."""
        self.config = config or ProvinceGenerationConfig()
        self.analyzer = ProvinceAnalyzer()
        self.island_analysis = None
        
    def _is_valid_province(self, province: ProvinceData) -> bool:
        """Проверяет валидность провинции."""
        # Проверяем размер
        if len(province.cells) < self.config.min_province_size:
            return False
        if len(province.cells) > self.config.max_province_size:
            return False
            
        # Проверяем связность
        visited = self._get_connected_cells(next(iter(province.cells)), province.cells)
        if len(visited) != len(province.cells):
            return False
            
        # Проверяем плюсовые пересечения если включено
        if self.config.check_plus_intersection:
            for cell in province.cells:
                if self._has_plus_intersection(cell, province.cells):
                    return False
                    
        return True
        
    def _get_connected_cells(self, start: Tuple[int, int], cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Возвращает все связанные клетки из данного множества, начиная с заданной."""
        visited = {start}
        queue = deque([start])
        
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor in cells and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        return visited
        
    def _has_plus_intersection(self, cell: Tuple[int, int], cells: Set[Tuple[int, int]]) -> bool:
        """Проверяет наличие плюсового пересечения в данной точке."""
        x, y = cell
        pattern = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Верх, право, низ, лево
        matches = [(x + dx, y + dy) in cells for dx, dy in pattern]
        return all(matches)  # Если все 4 направления заняты, это плюс
        
    def _fix_province(self, province: ProvinceData) -> bool:
        """Пытается исправить невалидную провинцию."""
        if len(province.cells) < self.config.min_province_size:
            # Пытаемся расширить провинцию
            needed = self.config.min_province_size - len(province.cells)
            border = self._get_border_cells(province.cells)
            while needed > 0 and border:
                cell = self._choose_best_expansion_cell(border, province.cells)
                if cell:
                    province.cells.add(cell)
                    border = self._get_border_cells(province.cells)
                    needed -= 1
                else:
                    break
                    
        elif len(province.cells) > self.config.max_province_size:
            # Удаляем лишние клетки
            while len(province.cells) > self.config.max_province_size:
                cell = self._choose_removal_candidate(province.cells)
                if cell:
                    province.cells.remove(cell)
                else:
                    break
                    
        # Проверяем и исправляем связность
        if not self._is_fully_connected(province.cells):
            self._fix_connectivity(province)
            
        # Проверяем и исправляем плюсовые пересечения
        if self.config.check_plus_intersection:
            self._fix_plus_intersections(province)
            
        return self._is_valid_province(province)
        
    def _get_border_cells(self, cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Возвращает множество граничных клеток вокруг провинции."""
        border = set()
        for x, y in cells:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if (0 <= neighbor[0] < GRID_WIDTH and 
                    0 <= neighbor[1] < GRID_HEIGHT and
                    neighbor not in cells):
                    border.add(neighbor)
        return border
        
    def _choose_best_expansion_cell(self, border: Set[Tuple[int, int]], 
                                  current_cells: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Выбирает лучшую клетку для расширения провинции."""
        if not border:
            return None
            
        best_cell = None
        best_score = float('-inf')
        
        for cell in border:
            # Проверяем, не создаст ли добавление этой клетки плюс
            if self.config.check_plus_intersection:
                temp_cells = current_cells | {cell}
                if self._has_plus_intersection(cell, temp_cells):
                    continue
                    
            # Считаем метрики для оценки клетки
            neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                          if (cell[0] + dx, cell[1] + dy) in current_cells)
            
            # Вычисляем центр текущих клеток
            cx = sum(x for x, _ in current_cells) / len(current_cells)
            cy = sum(y for _, y in current_cells) / len(current_cells)
            
            # Расстояние до центра
            dx = cell[0] - cx
            dy = cell[1] - cy
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Итоговый скор
            score = (neighbors * self.config.weights['neighbor_count'] -
                    distance * self.config.weights['center_distance'])
                    
            if score > best_score:
                best_score = score
                best_cell = cell
                
        return best_cell
        
    def _choose_removal_candidate(self, cells: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Выбирает клетку для удаления, сохраняя связность."""
        border_cells = {
            cell for cell in cells
            if any((cell[0] + dx, cell[1] + dy) not in cells
                  for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)])
        }
        
        for cell in border_cells:
            # Временно удаляем клетку
            cells.remove(cell)
            if self._is_fully_connected(cells):
                return cell
            cells.add(cell)
            
        return None
        
    def _is_fully_connected(self, cells: Set[Tuple[int, int]]) -> bool:
        """Проверяет полную связность множества клеток."""
        if not cells:
            return True
            
        start = next(iter(cells))
        connected = self._get_connected_cells(start, cells)
        return len(connected) == len(cells)
        
    def _fix_connectivity(self, province: ProvinceData) -> None:
        """Исправляет связность провинции."""
        if not province.cells:
            return

        # Находим самый большой связный компонент
        start = next(iter(province.cells))
        largest_component = self._get_connected_cells(start, province.cells)
        
        while len(province.cells) > len(largest_component):
            # Находим клетки в других компонентах
            disconnected = province.cells - largest_component
            
            # Пытаемся соединить компоненты
            best_connection = None
            best_score = float('-inf')
            
            for cell1 in largest_component:
                for cell2 in disconnected:
                    # Находим путь между клетками
                    path = self._find_connecting_path(cell1, cell2, province.cells)
                    if path:
                        # Оцениваем качество соединения
                        score = -len(path)  # Предпочитаем короткие пути
                        score += sum(self._evaluate_cell_score((x, y), largest_component)
                                for x, y in path)
                        
                        if score > best_score:
                            best_score = score
                            best_connection = path
            
            if best_connection:
                # Добавляем соединяющий путь
                largest_component.update(best_connection)
                province.cells.update(best_connection)
            else:
                # Если не можем соединить, удаляем отсоединенную часть
                province.cells = largest_component
                break

    def _find_connecting_path(self, start: Tuple[int, int], end: Tuple[int, int], 
                            blocked: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Находит путь между двумя клетками, избегая занятых клеток."""
        if start == end:
            return {start}

        visited = {start}
        queue = deque([(start, {start})])
        
        while queue:
            current, path = queue.popleft()
            x, y = current
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_pos = (x + dx, y + dy)
                if (next_pos not in visited and 
                    next_pos not in blocked and
                    0 <= next_pos[0] < GRID_WIDTH and 
                    0 <= next_pos[1] < GRID_HEIGHT):
                    
                    new_path = path | {next_pos}
                    if next_pos == end:
                        return new_path
                        
                    visited.add(next_pos)
                    queue.append((next_pos, new_path))
        
        return set()