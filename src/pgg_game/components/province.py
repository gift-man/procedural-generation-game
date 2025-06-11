"""Компонент провинции."""
import random
from typing import Set, List, Tuple, Dict, Optional
from dataclasses import dataclass, field
from ..world.generators.province_settings import ProvinceGenerationConfig

@dataclass
class ProvinceData:
    """Класс для хранения данных о провинции."""
    cells: Set[Tuple[int, int]] = field(default_factory=set)  # Клетки провинции
    neighbors: Set[int] = field(default_factory=set)          # ID соседних провинций
    border_cells: Set[Tuple[int, int]] = field(default_factory=set)  # Граничные клетки
    target_size: Optional[int] = None  # Целевой размер провинции

class ProvinceManager:
    """Менеджер провинций для соблюдения всех условий."""
    
    def __init__(self, config: Optional[ProvinceGenerationConfig] = None):
        """
        Инициализация менеджера.
        
        Args:
            config: Настройки генерации провинций
        """
        self.provinces: Dict[int, ProvinceData] = {}
        self.cell_to_province: Dict[Tuple[int, int], int] = {}
        self.next_province_id = 0
        self.config = config or ProvinceGenerationConfig()

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
        Добавляет клетку в провинцию с проверкой всех условий.
        
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
        if self._would_create_plus_intersection(province_id, cell):
            return False

        # Проверяем связность
        if not self._would_maintain_connectivity(province_id, cell):
            return False

        # Добавляем клетку
        province.cells.add(cell)
        self.cell_to_province[cell] = province_id
        self._update_borders(province_id)
        return True

    def _would_create_plus_intersection(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """
        Проверяет, создаст ли добавление клетки плюсовое пересечение.
        
        Args:
            province_id: ID провинции
            cell: Координаты клетки (x, y)
            
        Returns:
            bool: True если создаст плюсовое пересечение
        """
        x, y = cell
        # Проверяем центральное пересечение ┼
        patterns = [
            [(0, 0), (0, -1), (1, 0), (0, 1), (-1, 0)]
        ]
        
        for pattern in patterns:
            provinces_in_pattern = set()
            for dx, dy in pattern:
                check_cell = (x + dx, y + dy)
                if check_cell == cell:
                    provinces_in_pattern.add(province_id)
                else:
                    prov_id = self.cell_to_province.get(check_cell)
                    if prov_id is not None:
                        provinces_in_pattern.add(prov_id)
            
            if len(provinces_in_pattern) >= len(pattern):
                return True
        return False

    def _would_maintain_connectivity(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """
        Проверяет, сохранит ли добавление клетки связность провинции.
        
        Args:
            province_id: ID провинции
            cell: Координаты клетки (x, y)
            
        Returns:
            bool: True если клетка будет соединена с провинцией
        """
        if not self.provinces[province_id].cells:
            return True

        x, y = cell
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if neighbor in self.provinces[province_id].cells:
                return True
        return False

    def _update_borders(self, province_id: int) -> None:
        """
        Обновляет границы провинции.
        
        Args:
            province_id: ID провинции
        """
        province = self.provinces[province_id]
        province.border_cells.clear()

        for cell in province.cells:
            x, y = cell
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor not in province.cells:
                    province.border_cells.add(cell)
                    break

    def get_ideal_province_size(self) -> int:
        """
        Возвращает случайный размер провинции по заданным вероятностям.
        
        Returns:
            int: Размер провинции от 4 до 8 клеток
        """
        sizes = {
            4: 0.15,  # 15% шанс
            5: 0.20,  # 20% шанс  
            6: 0.30,  # 30% шанс
            7: 0.20,  # 20% шанс
            8: 0.15   # 15% шанс
        }
        
        rand = random.random()
        cumulative = 0.0
        for size, prob in sizes.items():
            cumulative += prob
            if rand <= cumulative:
                return size
        return 6  # По умолчанию размер 6