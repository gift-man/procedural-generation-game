"""Менеджер провинций."""
import random
from typing import Set, Dict, Tuple, Optional, List
from ..world.generators.province_settings import ProvinceGenerationConfig
from collections import deque
from ..components.province import ProvinceData, Province  # Добавляем импорт Province

class ProvinceManager:
    """Управляет провинциями на карте."""
        
    def __init__(self, config: Optional[ProvinceGenerationConfig] = None):
        """
        Инициализация менеджера провинций.
        
        Args:
            config: Настройки генерации провинций
        """
        self.provinces: Dict[int, ProvinceData] = {}
        self.cell_to_province: Dict[Tuple[int, int], int] = {}
        self.next_province_id = 0
        self.config = config or ProvinceGenerationConfig()

    def get_province_cells(self, province_id: int) -> Set[Tuple[int, int]]:
        """
        Возвращает клетки провинции.
        
        Args:
            province_id: ID провинции
            
        Returns:
            Set[Tuple[int, int]]: Множество клеток провинции
        """
        if province_id in self.provinces:
            return set(self.provinces[province_id].cells)
        return set()
    
    def get_provinces(self) -> List[Province]:
        """
        Возвращает список провинций.
        
        Returns:
            List[Province]: Список провинций
        """
        result = []
        for pid, data in self.provinces.items():
            province = Province(id=pid, cells=set(data.cells))
            province.province_data = data
            result.append(province)
        return result
    
    def get_ideal_province_size(self) -> int:
        """
        Возвращает размер провинции на основе вероятностей из конфигурации.
        
        Returns:
            int: Размер провинции от 4 до 8 клеток
        """
        rand = random.random()
        cumulative = 0.0
        
        for size, prob in self.config.size_probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                return size
                
        # По умолчанию возвращаем средний размер
        return 6

    def create_province(self, target_size: Optional[int] = None) -> int:
        """
        Создает новую провинцию.
        
        Args:
            target_size: Желаемый размер провинции
            
        Returns:
            int: ID новой провинции
        """
        province_id = self.next_province_id
        self.next_province_id += 1
        self.provinces[province_id] = ProvinceData(target_size=target_size)
        return province_id
    
    def add_cell_to_province(self, province_id: int, cell: Tuple[int, int]) -> bool:
            """
            Добавляет клетку в провинцию.
            
            Args:
                province_id: ID провинции
                cell: Координаты клетки (x, y)
                
            Returns:
                bool: True если клетка успешно добавлена
            """
            if cell in self.cell_to_province:
                return False
                
            province = self.provinces[province_id]
            
            # Проверяем целевой размер
            if (province.target_size is not None and 
                len(province.cells) >= province.target_size):
                return False
                
            # Проверяем создание плюсового пересечения
            if self.config.check_plus_intersection:
                if self._would_create_plus_intersection(province_id, cell):
                    return False
                
            # Проверка связности для существующей провинции
            if not self._would_maintain_connectivity(province_id, cell):
                return False
            
            # Добавляем клетку
            province.cells.add(cell)
            self.cell_to_province[cell] = province_id
            
            # Обновляем метрики провинции
            province.update_metrics()
            return True
    
    def _would_create_plus_intersection(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """Проверяет, создаст ли добавление клетки плюсовое пересечение."""
        x, y = cell
        # Проверяем только центральное пересечение ┼
        pattern = [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
        
        provinces_in_pattern = set()
        for dx, dy in pattern:
            check_cell = (x + dx, y + dy)
            if check_cell == cell:
                provinces_in_pattern.add(province_id)
            elif check_cell in self.cell_to_province:
                provinces_in_pattern.add(self.cell_to_province[check_cell])
        
        return len(provinces_in_pattern) == len(pattern)

    def _would_maintain_connectivity(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """Проверяет, сохранит ли добавление клетки связность провинции."""
        if not self.provinces[province_id].cells:
            return True
            
        x, y = cell
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if neighbor in self.provinces[province_id].cells:
                return True
        return False


    def validate_province(self, province_id: int) -> bool:
        """
        Проверяет корректность провинции.
        """
        province = self.provinces[province_id]
        
        # Проверка размера
        if len(province.cells) < self.config.min_province_size:
            return False
        if len(province.cells) > self.config.max_province_size:
            return False
            
        # Проверка связности
        if not self._check_connectivity(province_id):
            return False
            
        # Проверка плюсовых пересечений
        if self.config.check_plus_intersection:
            for cell in province.cells:
                if self._would_create_plus_intersection(province_id, cell):
                    return False
                    
        return True

    def _check_connectivity(self, province_id: int) -> bool:
        """
        Проверяет связность провинции через обход в ширину.
        """
        province = self.provinces[province_id]
        if not province.cells:
            return True
            
        start = next(iter(province.cells))
        visited = {start}
        queue = deque([start])
        
        while queue:
            current = queue.popleft()
            x, y = current
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if (neighbor in province.cells and 
                    neighbor not in visited):
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        return len(visited) == len(province.cells)