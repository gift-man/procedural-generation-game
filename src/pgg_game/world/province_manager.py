"""Менеджер провинций."""
import random
from typing import Set, Dict, Tuple, Optional, List
from collections import deque
from ..components.province import ProvinceData, Province
from ..world.generators.province_settings import ProvinceGenerationConfig

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
        
        # Устанавливаем конфигурацию
        self.config = config or ProvinceGenerationConfig()
        self.growth_attempts = 0
        self.max_growth_attempts = 100  # Предотвращаем бесконечный цикл
        
        # Проверяем наличие вероятностей размеров в конфигурации
        if not hasattr(self.config, 'size_probabilities'):
            self.config.size_probabilities = {
                4: 0.20,  # 20% шанс для провинций размером 4
                5: 0.25,  # 25% шанс для провинций размером 5
                6: 0.25,  # 25% шанс для провинций размером 6
                7: 0.20,  # 20% шанс для провинций размером 7
                8: 0.10   # 10% шанс для провинций размером 8
            }
        
    def _reset_growth_attempts(self):
        """Сбрасывает счетчик попыток роста."""
        self.growth_attempts = 0
        
    def _increment_growth_attempts(self) -> bool:
        """Увеличивает счетчик попыток роста и проверяет лимит."""
        self.growth_attempts += 1
        return self.growth_attempts < self.max_growth_attempts
        
    def get_provinces(self) -> List[Province]:
        """Возвращает список провинций."""
        return [Province(id=pid, cells=set(data.cells)) 
                for pid, data in self.provinces.items()]
                
    def create_province(self, target_size: Optional[int] = None) -> int:
        """Создает новую провинцию."""
        province_id = self.next_province_id
        self.next_province_id += 1
        self.provinces[province_id] = ProvinceData(target_size=target_size)
        self._reset_growth_attempts()
        return province_id
        
    def add_cell_to_province(self, province_id: int, cell: Tuple[int, int], 
                            force: bool = False) -> bool:
        """Добавляет клетку в провинцию."""
        if not self._increment_growth_attempts():
            return False
            
        if cell in self.cell_to_province and not force:
            return False
            
        province = self.provinces[province_id]
        
        # Проверяем целевой размер
        if (province.target_size is not None and 
            len(province.cells) >= province.target_size and 
            not force):
            return False
            
        # Если это первая клетка, всегда добавляем
        if not province.cells:
            province.cells.add(cell)
            self.cell_to_province[cell] = province_id
            province.update_metrics()
            return True
            
        # Проверяем создание плюсового пересечения
        if self.config.check_plus_intersection and not force:
            if self._would_create_plus_intersection(province_id, cell):
                return False
            
        # Проверяем связность
        if not self._has_valid_connection(province_id, cell) and not force:
            return False
            
        # Добавляем клетку
        province.cells.add(cell)
        self.cell_to_province[cell] = province_id
        
        # Обновляем метрики провинции
        province.update_metrics()
        return True
        
    def _has_valid_connection(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """Проверяет, имеет ли клетка действительное соединение с провинцией."""
        province = self.provinces[province_id]
        x, y = cell
        
        # Проверяем наличие хотя бы одного соседа из той же провинции
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if neighbor in province.cells:
                return True
        return False
        
    def _would_create_plus_intersection(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """Проверяет, создаст ли добавление клетки плюсовое пересечение."""
        x, y = cell
        
        # Проверяем все четыре направления
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # верх, право, низ, лево
        neighbors = []
        
        for dx, dy in directions:
            neighbor = (x + dx, y + dy)
            if neighbor in self.cell_to_province:
                neighbor_province = self.cell_to_province[neighbor]
                if neighbor_province != province_id:
                    neighbors.append(neighbor_province)
                    
        # Если есть клетки от трех разных провинций вокруг, 
        # это создаст плюсовое пересечение
        return len(set(neighbors)) >= 3
        
    def validate_provinces(self) -> bool:
        """Проверяет валидность всех провинций."""
        for pid in self.provinces:
            if not self.validate_province(pid):
                return False
        return True
        
    def validate_province(self, province_id: int) -> bool:
        """Проверяет валидность конкретной провинции."""
        province = self.provinces[province_id]
        
        # Проверка минимального размера
        if len(province.cells) < self.config.min_province_size:
            return False
            
        # Проверка максимального размера
        if len(province.cells) > self.config.max_province_size:
            return False
            
        # Проверка связности
        if not self._check_connectivity(province_id):
            return False
            
        # Проверка отсутствия плюсовых пересечений
        if self.config.check_plus_intersection:
            for cell in province.cells:
                # Временно убираем клетку из провинции для проверки
                old_province = self.cell_to_province.get(cell)
                if old_province is not None:
                    del self.cell_to_province[cell]
                
                has_plus = self._would_create_plus_intersection(province_id, cell)
                
                # Возвращаем клетку обратно
                if old_province is not None:
                    self.cell_to_province[cell] = old_province
                    
                if has_plus:
                    return False
                    
        return True
        
    def _check_connectivity(self, province_id: int) -> bool:
        """Проверяет связность провинции."""
        province = self.provinces[province_id]
        if not province.cells:
            return True
            
        # Начинаем с первой клетки
        start = next(iter(province.cells))
        visited = {start}
        queue = deque([start])
        
        # Обход в ширину
        while queue:
            current = queue.popleft()
            x, y = current
            
            # Проверяем все соседние клетки
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if (neighbor in province.cells and 
                    neighbor not in visited):
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        # Все клетки должны быть достижимы
        return len(visited) == len(province.cells)
    def get_ideal_province_size(self) -> int:
        """
        Возвращает размер провинции на основе вероятностей из конфигурации.
        
        Returns:
            int: Размер провинции
        """
        rand = random.random()
        cumulative = 0.0
        
        # Используем вероятности из конфигурации
        for size, prob in self.config.size_probabilities.items():
            cumulative += prob
            if rand <= cumulative:
                return size
                
        # По умолчанию возвращаем средний размер
        return 6
    
    def get_available_province_sizes(self) -> List[int]:
        """
        Возвращает список доступных размеров провинций.
        
        Returns:
            List[int]: Список размеров провинций
        """
        return sorted(self.config.size_probabilities.keys())