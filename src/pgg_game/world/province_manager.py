"""Менеджер провинций."""
from typing import Set, Dict, Tuple, Optional
from ..components.province_info import ProvinceInfoComponent

class ProvinceManager:
    """Управляет провинциями на карте."""
        
    def __init__(self):
        """Инициализация менеджера провинций."""
        self.provinces: Dict[int, Set[Tuple[int, int]]] = {}
        self.cell_to_province: Dict[Tuple[int, int], int] = {}
        self.next_province_id = 0
        self._min_province_size = 4  # Минимальный размер провинции
        self._max_province_size = 8  # Максимальный размер провинции
        
    def create_province(self) -> int:
        """
        Создает новую провинцию.
        
        Returns:
            int: ID новой провинции
        """
        province_id = self.next_province_id
        self.next_province_id += 1
        self.provinces[province_id] = set()  # Создаем пустое множество для клеток
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
            
        if province_id not in self.provinces:
            self.provinces[province_id] = set()
        
        current_size = len(self.provinces[province_id])
        
        # Проверяем размер провинции
        if current_size >= self._max_province_size:
            return False
        
        # Проверка связности для существующей провинции
        if current_size > 0 and not self._would_maintain_connectivity(province_id, cell):
            return False
        
        # Добавляем клетку
        self.provinces[province_id].add(cell)
        self.cell_to_province[cell] = province_id
        return True
    
    def get_border_cells(self, province_id: int) -> Set[Tuple[int, int]]:
        """
        Возвращает множество граничных клеток провинции.
        
        Args:
            province_id: ID провинции
            
        Returns:
            Set[Tuple[int, int]]: Множество координат граничных клеток
        """
        if province_id not in self.provinces:
            return set()
            
        border_cells = set()
        for cell in self.provinces[province_id]:
            x, y = cell
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor not in self.provinces[province_id]:
                    border_cells.add(cell)
                    break
        return border_cells
    
    def _would_create_plus_intersection(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """Проверяет, создаст ли добавление клетки плюсовое пересечение."""
        x, y = cell
        corners = [
            [(x-1, y-1), (x, y-1), (x-1, y), (x, y)],
            [(x, y-1), (x+1, y-1), (x, y), (x+1, y)],
            [(x-1, y), (x, y), (x-1, y+1), (x, y+1)],
            [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
        ]
        
        for corner_cells in corners:
            provinces_at_corner = set()
            for cx, cy in corner_cells:
                if (cx, cy) == cell:
                    provinces_at_corner.add(province_id)
                elif (cx, cy) in self.cell_to_province:
                    provinces_at_corner.add(self.cell_to_province[(cx, cy)])
            
            if len(provinces_at_corner) >= 4:
                return True
        return False
    
    def _would_maintain_connectivity(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """Проверяет, сохранит ли добавление клетки связность провинции."""
        if not self.provinces[province_id]:
            return True
            
        x, y = cell
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if neighbor in self.provinces[province_id]:
                return True
        return False