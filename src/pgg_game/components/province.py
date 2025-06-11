"""Компонент провинции."""
from typing import Set, List, Tuple, Dict
from dataclasses import dataclass, field

@dataclass
class ProvinceData:
    """Класс для хранения данных о провинции."""
    cells: Set[Tuple[int, int]] = field(default_factory=set)  # Клетки провинции
    neighbors: Set[int] = field(default_factory=set)          # ID соседних провинций
    border_cells: Set[Tuple[int, int]] = field(default_factory=set)  # Граничные клетки

class ProvinceManager:
    """Менеджер провинций для соблюдения всех условий."""
    def __init__(self):
        self.provinces: Dict[int, ProvinceData] = {}
        self.cell_to_province: Dict[Tuple[int, int], int] = {}
        self.next_province_id = 0

    def create_province(self) -> int:
        """Создает новую провинцию."""
        province_id = self.next_province_id
        self.next_province_id += 1
        self.provinces[province_id] = ProvinceData()
        return province_id

    def add_cell_to_province(self, province_id: int, cell: Tuple[int, int]) -> bool:
        """
        Добавляет клетку в провинцию с проверкой всех условий.
        
        Returns:
            bool: True если клетка успешно добавлена
        """
        if cell in self.cell_to_province:
            return False

        # Проверяем размер провинции
        if len(self.provinces[province_id].cells) >= 12:  # MAX_PROVINCE_SIZE
            return False

        # Проверяем создание плюсового пересечения
        if self._would_create_plus_intersection(province_id, cell):
            return False

        # Проверяем связность
        if not self._would_maintain_connectivity(province_id, cell):
            return False

        # Добавляем клетку
        self.provinces[province_id].cells.add(cell)
        self.cell_to_province[cell] = province_id
        self._update_borders(province_id)
        return True

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
        if not self.provinces[province_id].cells:
            return True

        # Проверяем, есть ли сосед из той же провинции
        x, y = cell
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if neighbor in self.provinces[province_id].cells:
                return True
        return False

    def _update_borders(self, province_id: int) -> None:
        """Обновляет границы провинции."""
        province = self.provinces[province_id]
        province.border_cells.clear()

        for cell in province.cells:
            x, y = cell
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor not in province.cells:
                    province.border_cells.add(cell)
                    break