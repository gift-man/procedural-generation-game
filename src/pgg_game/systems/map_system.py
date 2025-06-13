"""
Система генерации и управления игровой картой.
"""
import numpy as np
import pygame
from typing import Set, Tuple, Dict, Optional
from collections import deque

from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    GRID_WIDTH, GRID_HEIGHT,
    TILE_SIZE, COLORS,
    RENDER_LAYERS,
    BORDER_THICKNESS
)
from ..world.game_world import GameWorld
from ..world.province_manager import ProvinceManager
from ..components.transform import TransformComponent
from ..components.renderable import RenderableComponent
from ..components.province_info import ProvinceInfoComponent

class MapSystem:
    """Система управления картой."""

    def __init__(self):
        """Инициализация системы карты."""
        self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=np.int32)
        self.provinces = {}  
        self.cell_to_province = {}
        self.world = None
        self.map_generated = False
        
        # Создаем менеджер провинций
        self.province_manager = ProvinceManager()
        
        # Создаем поверхность для карты
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def update(self, world: GameWorld) -> None:
        """
        Обновление состояния карты.
        
        Args:
            world: Игровой мир
        """
        self.world = world
        
        if not self.map_generated:
            self.generate_map(world)
            self.map_generated = True

    def generate_map(self, world: GameWorld) -> None:
        """Генерирует новую карту."""
        try:
            for attempt in range(5):
                print(f"Попытка генерации {attempt + 1}")
                
                if self._generate_from_provinces():
                    if self._create_province_entities(world):
                        self.map_generated = True
                        print("Карта успешно сгенерирована")
                        return
                
                print(f"Попытка {attempt + 1} не удалась")
                
            raise RuntimeError("Не удалось сгенерировать карту")
        except Exception as e:
            print(f"Ошибка при генерации карты: {e}")
            raise



    def _generate_provinces(self) -> bool:
        """Генерирует провинции на карте."""
        # Находим клетки суши
        land_cells = {(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) 
                     if self.grid[y, x] == 1}
        
        if not land_cells:
            return False
        
        # Настраиваем количество и размеры провинций
        total_land = len(land_cells)
        min_provinces = max(3, total_land // 25)  # ~25 клеток на провинцию
        max_provinces = min(8, total_land // 15)  # ~15 клеток на провинцию
        min_size = max(4, total_land // (max_provinces * 2))
        max_size = min(25, total_land // min_provinces)
        
        # Обновляем конфигурацию
        self.province_manager.config.update(
            min_provinces=min_provinces,
            max_provinces=max_provinces,
            min_size=min_size,
            max_size=max_size
        )
        
        # Генерируем провинции
        return self._create_provinces(land_cells)

    def _create_provinces(self, land_cells: Set[Tuple[int, int]]) -> bool:
        """Создает провинции из доступных клеток."""
        unassigned_cells = land_cells.copy()
        center_x = sum(x for x, _ in land_cells) / len(land_cells)
        center_y = sum(y for _, y in land_cells) / len(land_cells)
        
        while unassigned_cells:
            start = self._find_best_start_point(unassigned_cells, (center_x, center_y))
            if not start:
                break
                
            # Создаем новую провинцию
            province_id = self.province_manager.create_province()
            target_size = self.province_manager.get_ideal_province_size()
            
            # Выращиваем провинцию из стартовой точки
            cells = self._grow_province_from_center(start, target_size, unassigned_cells)
            
            # Добавляем клетки в провинцию
            for cell in cells:
                if self.province_manager.add_cell_to_province(province_id, cell):
                    unassigned_cells.remove(cell)
        
        # Проверяем результат
        if not unassigned_cells and self._verify_provinces():
            return True
            
        return False

    def _find_best_start_point(
        self, 
        cells: Set[Tuple[int, int]], 
        center: Tuple[float, float]
    ) -> Optional[Tuple[int, int]]:
        """Находит лучшую стартовую точку для новой провинции."""
        if not cells:
            return None
            
        best_point = None
        best_score = float('-inf')
        cx, cy = center
        
        for x, y in cells:
            # Расстояние до центра (ближе = лучше)
            dist = -((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            
            # Количество соседей
            neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                          if (x + dx, y + dy) in cells)
            
            score = dist + neighbors * 2
            
            if score > best_score:
                best_score = score
                best_point = (x, y)
                
        return best_point

    def _grow_province_from_center(
        self,
        start: Tuple[int, int],
        target_size: int,
        available_cells: Set[Tuple[int, int]]
    ) -> Set[Tuple[int, int]]:
        """Выращивает провинцию из начальной точки."""
        province = {start}
        frontier = {start}
        
        while len(province) < target_size and frontier:
            best_cell = None
            best_score = float('-inf')
            
            for cell in frontier:
                x, y = cell
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    neighbor = (x + dx, y + dy)
                    if neighbor not in available_cells or neighbor in province:
                        continue
                        
                    # Считаем соседей
                    neighbors = sum(
                        1 for nx, ny in [(neighbor[0] + dx, neighbor[1] + dy) 
                                       for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]]
                        if (nx, ny) in province
                    )
                    
                    # Оцениваем компактность
                    cx = sum(x for x, _ in province) / len(province)
                    cy = sum(y for _, y in province) / len(province)
                    distance = ((neighbor[0] - cx) ** 2 + (neighbor[1] - cy) ** 2) ** 0.5
                    
                    score = neighbors - (distance * 0.5)
                    
                    if score > best_score:
                        best_score = score
                        best_cell = neighbor
            
            if best_cell is None:
                break
                
            province.add(best_cell)
            frontier.add(best_cell)
            
            # Обновляем фронтир
            frontier = {cell for cell in frontier 
                      if any((cell[0] + dx, cell[1] + dy) not in province
                            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)])}
        
        return province

    def _verify_provinces(self) -> bool:
        """Проверяет корректность всех провинций."""
        for province in self.province_manager.provinces.values():
            # Проверка размера
            if not (self.province_manager.config.min_size <= 
                   len(province.cells) <= 
                   self.province_manager.config.max_size):
                return False
            
            # Проверка связности
            if len(self._get_connected_cells(
                next(iter(province.cells)),
                province.cells
            )) != len(province.cells):
                return False
            
            # Проверка соседей
            if not all(
                any((x + dx, y + dy) in province.cells
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)])
                for x, y in province.cells
            ):
                return False
        
        return True

    def _get_connected_cells(
        self,
        start: Tuple[int, int],
        cells: Set[Tuple[int, int]]
    ) -> Set[Tuple[int, int]]:
        """Находит все связанные клетки."""
        if not cells:
            return set()
            
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

    def _create_province_entities(self, world: GameWorld) -> bool:
        """Создает сущности для провинций."""
        if not hasattr(self, 'province_manager'):
            return False
            
        provinces = self.province_manager.get_provinces()
        
        for province in provinces:
            if not province.cells:
                continue
                
            # Вычисляем размеры и позицию
            min_x = min(x for x, _ in province.cells)
            min_y = min(y for _, y in province.cells)
            max_x = max(x for x, _ in province.cells)
            max_y = max(y for _, y in province.cells)
            width = max_x - min_x + 1
            height = max_y - min_y + 1
            
            # Создаем сущность
            entity_id = world.create_entity()
            
            # Добавляем компоненты
            world.add_component(
                entity_id,
                TransformComponent(x=min_x, y=min_y)
            )
            
            world.add_component(
                entity_id,
                RenderableComponent(
                    color=COLORS['province_neutral'],
                    width=width,
                    height=height,
                    border_width=2,
                    border_color=COLORS['province_border'],
                    layer=RENDER_LAYERS['provinces']
                )
            )
            
            province_info = ProvinceInfoComponent(f"Province {province.id}")
            province_info.cells = set(province.cells)
            world.add_component(entity_id, province_info)
            
        return True

    def render(self, world: GameWorld) -> None:
        """Отрисовывает карту."""
        # Заливаем фон водой
        self.surface.fill(COLORS['water'])
        
        # Отрисовка клеток
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                
                if self.grid[y, x] == 1:
                    pygame.draw.rect(self.surface, COLORS['province_neutral'], rect)
                pygame.draw.rect(self.surface, COLORS['grid'], rect, 1)
        
        # Отрисовка границ провинций
        for province_id, province in self.province_manager.provinces.items():
            for x, y in province.cells:
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (nx, ny) not in province.cells:
                        start_pos = (x * TILE_SIZE, y * TILE_SIZE)
                        if dx == 1:  # Правая граница
                            end_pos = (start_pos[0] + TILE_SIZE, start_pos[1])
                        elif dx == -1:  # Левая граница
                            end_pos = (start_pos[0], start_pos[1] + TILE_SIZE)
                        elif dy == 1:  # Нижняя граница
                            end_pos = (start_pos[0] + TILE_SIZE, start_pos[1] + TILE_SIZE)
                        else:  # Верхняя граница
                            end_pos = (start_pos[0], start_pos[1])
                            
                        pygame.draw.line(
                            self.surface,
                            COLORS['province_border'],
                            start_pos,
                            end_pos,
                            2
                        )

    def get_surface(self) -> pygame.Surface:
        """Получает поверхность с отрисованной картой."""
        return self.surface