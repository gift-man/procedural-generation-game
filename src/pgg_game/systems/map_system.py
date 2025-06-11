"""
Система генерации и управления игровой картой.
"""
import random
from typing import List, Set, Tuple, Dict, Optional
import pygame
import sys

try:
    import numpy as np
except ImportError:
    print("\nОШИБКА: Библиотека numpy не установлена!")
    print("Для установки выполните команду:")
    print("pip install numpy>=1.24.0")
    sys.exit(1)

from ..world.province_manager import ProvinceManager
from ..world.game_world import GameWorld
from ..components.transform import TransformComponent
from ..components.renderable import RenderableComponent
from ..components.province_info import ProvinceInfoComponent
from ..components.resource import ResourceComponent, ResourceType
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE,
    GRID_WIDTH, GRID_HEIGHT, COLORS,
    RENDER_LAYERS,
    BORDER_THICKNESS,
    PROVINCE_BORDER_THICKNESS,
    PROVINCE_BORDER_DASH_LENGTH,
    PROVINCE_BORDER_GAP_LENGTH
)

class MapSystem:
    """Система управления картой."""
    
    def __init__(self):
        """Инициализация системы карты."""
        self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=np.int32)
        self.provinces = {}  # Словарь провинций
        self.cell_to_province = {}  # Маппинг клеток к провинциям
        self.resources = {}  # Словарь ресурсов
        self.world = None
        self.map_generated = False
        
        # Настройки генерации
        self.min_province_size = 4
        self.max_province_size = 8
        self.min_island_size = 40
        self.max_island_size = 80
        
        # Настройки ресурсов
        self.resource_clusters = {
            ResourceType.GOLD: {'min_size': 1, 'chance': 0.15},
            ResourceType.STONE: {'min_size': 2, 'chance': 0.25},
            ResourceType.WOOD: {'min_size': 4, 'chance': 0.35},
            ResourceType.FOOD: {'min_size': 1, 'chance': 1.0}
        }

        # Создаем поверхность для карты
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Создаем менеджер провинций
        self.province_manager = ProvinceManager()

    def update(self, world: GameWorld) -> None:
        """
        Обновление состояния карты.
        
        Args:
            world: Игровой мир
        """
        self.world = world
        
        # Генерируем карту только один раз
        if not self.map_generated:
            self.generate_map(world)
            self.map_generated = True
    
    def generate_map(self, world: GameWorld) -> None:
        """
        Генерирует новую карту.
        
        Args:
            world: Игровой мир
        """
        # 1. Очищаем карту
        self.grid.fill(0)
        self.provinces.clear()
        self.resources.clear()
        
        # 2. Генерируем основной остров
        self._generate_islands()
        
        # 3. Разделяем на провинции
        self.generate_provinces()  # Изменено с _generate_provinces() на generate_provinces()
        
        # 4. Генерируем ресурсы
        self._generate_resources()
        
        # 5. Создаем сущности для провинций
        self._create_province_entities(world)

        # После успешной генерации карты
        self.map_generated = True
    
    def _generate_islands(self) -> None:
        """Генерирует острова на карте."""
        # Центр карты
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        
        # Генерируем основной остров
        island_size = random.randint(self.min_island_size, self.max_island_size)
        cells = set()
        
        # Начинаем с центральной точки
        cells.add((center_x, center_y))
        
        # Расширяем остров
        while len(cells) < island_size:
            x, y = random.choice(list(cells))
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (0 < new_x < GRID_WIDTH - 1 and 
                    0 < new_y < GRID_HEIGHT - 1 and
                    (new_x, new_y) not in cells):
                    cells.add((new_x, new_y))
                    break
        
        # Применяем остров на сетку
        for x, y in cells:
            self.grid[y, x] = 1
    
   
    
    def _generate_resources(self) -> None:
        """Генерирует ресурсы на карте."""
        # Сначала заполняем всё лугами
        for province in self.provinces.values():
            for x, y in province:
                self.resources[(x, y)] = ResourceType.FOOD
        
        # Генерируем кластеры других ресурсов
        for resource_type, params in self.resource_clusters.items():
            if resource_type == ResourceType.FOOD:
                continue
                
            available_cells = set(
                cell for province in self.provinces.values()
                for cell in province
                if self.resources[cell] == ResourceType.FOOD
            )
            
            while available_cells:
                if random.random() > params['chance']:
                    break
                    
                start = random.choice(list(available_cells))
                cluster = self._grow_resource_cluster(
                    start[0], start[1],
                    params['min_size'],
                    available_cells
                )
                
                for cell in cluster:
                    self.resources[cell] = resource_type
                    available_cells.remove(cell)
    
    def _grow_resource_cluster(
        self,
        x: int,
        y: int,
        min_size: int,
        available_cells: Set[Tuple[int, int]]
    ) -> Set[Tuple[int, int]]:
        """Выращивает кластер ресурсов."""
        cluster = {(x, y)}
        frontier = [(x, y)]
        
        while frontier and len(cluster) < min_size:
            cx, cy = frontier.pop(0)
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = cx + dx, cy + dy
                if (new_x, new_y) in available_cells:
                    cluster.add((new_x, new_y))
                    frontier.append((new_x, new_y))
        
        return cluster
    
    def _get_province_color(self, province_id: int) -> Tuple[int, int, int]:
        """
        Возвращает цвет для провинции.
        
        Args:
            province_id: ID провинции
            
        Returns:
            Tuple[int, int, int]: RGB цвет
        """
        # Используем ID провинции для генерации уникального цвета
        r = (province_id * 67 + 100) % 156 + 100  # 100-255
        g = (province_id * 127 + 150) % 156 + 100  # 100-255
        b = (province_id * 191 + 200) % 156 + 100  # 100-255
        return (r, g, b)
    
    def render(self, world: GameWorld) -> None:
        """
        Отрисовка карты.
        """
        # 1. Заливаем фон водой
        self.surface.fill(COLORS['water'])
        
        # 2. Отрисовка клеток и их сетки
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                
                if self.grid[y, x] == 1:  # Если это суша
                    # Определяем тип ресурса и его цвета
                    resource_type = self.resources.get((x, y))
                    if resource_type:
                        base_name = resource_type.value
                    else:
                        base_name = 'food'  # По умолчанию еда

                    # Рисуем клетку
                    pygame.draw.rect(self.surface, COLORS[base_name], rect)
                    
                    # Рисуем сетку с цветом, соответствующим типу клетки
                    pygame.draw.rect(self.surface, COLORS[f'{base_name}_grid'], rect, 1)

                else:  # Если это вода
                    # Рисуем сетку воды
                    pygame.draw.rect(self.surface, COLORS['water_grid'], rect, 1)

        # 3. Отрисовка границы острова (толстая линия)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1:  # Если это суша
                    # Проверяем все соседние клетки
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        nx, ny = x + dx, y + dy
                        
                        # Если сосед - вода или за пределами карты
                        if (nx < 0 or nx >= GRID_WIDTH or 
                            ny < 0 or ny >= GRID_HEIGHT or 
                            self.grid[ny, nx] == 0):
                            
                            # Определяем начало и конец линии на границе между клетками
                            if dx == 0:  # Вертикальная граница
                                start_pos = (
                                    x * TILE_SIZE + (TILE_SIZE if dx > 0 else 0),
                                    y * TILE_SIZE
                                )
                                end_pos = (
                                    start_pos[0],
                                    y * TILE_SIZE + TILE_SIZE
                                )
                            else:  # Горизонтальная граница
                                start_pos = (
                                    x * TILE_SIZE,
                                    y * TILE_SIZE + (TILE_SIZE if dy > 0 else 0)
                                )
                                end_pos = (
                                    x * TILE_SIZE + TILE_SIZE,
                                    start_pos[1]
                                )
                            
                            # Рисуем толстую линию границы острова
                            pygame.draw.line(
                                self.surface,
                                COLORS['border_thick'],
                                start_pos,
                                end_pos,
                                BORDER_THICKNESS
                            )

        # 4. Отрисовка границ провинций (пунктирные линии)
        # Сначала горизонтальные границы
        for y in range(GRID_HEIGHT + 1):
            for x in range(GRID_WIDTH):
                # Только если обе клетки - суша
                if (y > 0 and y < GRID_HEIGHT and
                    self.grid[y-1, x] == 1 and 
                    self.grid[y, x] == 1):
                    
                    # Получаем ID провинций для клеток сверху и снизу
                    top_province = self.cell_to_province.get((x, y-1))
                    bottom_province = self.cell_to_province.get((x, y))
                    
                    # Если клетки принадлежат разным провинциям
                    if (top_province is not None and 
                        bottom_province is not None and 
                        top_province != bottom_province):
                        
                        # Рисуем пунктирную линию
                        x_start = x * TILE_SIZE
                        y_pos = y * TILE_SIZE
                        x_end = x_start + TILE_SIZE
                        
                        current_x = x_start
                        while current_x < x_end:
                            line_end = min(current_x + PROVINCE_BORDER_DASH_LENGTH, x_end)
                            pygame.draw.line(
                                self.surface,
                                COLORS['province_border'],
                                (current_x, y_pos),
                                (line_end, y_pos),
                                PROVINCE_BORDER_THICKNESS
                            )
                            current_x += PROVINCE_BORDER_DASH_LENGTH + PROVINCE_BORDER_GAP_LENGTH

        # Затем вертикальные границы
        for x in range(GRID_WIDTH + 1):
            for y in range(GRID_HEIGHT):
                # Только если обе клетки - суша
                if (x > 0 and x < GRID_WIDTH and
                    self.grid[y, x-1] == 1 and 
                    self.grid[y, x] == 1):
                    
                    # Получаем ID провинций для клеток слева и справа
                    left_province = self.cell_to_province.get((x-1, y))
                    right_province = self.cell_to_province.get((x, y))
                    
                    # Если клетки принадлежат разным провинциям
                    if (left_province is not None and 
                        right_province is not None and 
                        left_province != right_province):
                        
                        # Рисуем пунктирную линию
                        y_start = y * TILE_SIZE
                        x_pos = x * TILE_SIZE
                        y_end = y_start + TILE_SIZE
                        
                        current_y = y_start
                        while current_y < y_end:
                            line_end = min(current_y + PROVINCE_BORDER_DASH_LENGTH, y_end)
                            pygame.draw.line(
                                self.surface,
                                COLORS['province_border'],
                                (x_pos, current_y),
                                (x_pos, line_end),
                                PROVINCE_BORDER_THICKNESS
                            )
                            current_y += PROVINCE_BORDER_DASH_LENGTH + PROVINCE_BORDER_GAP_LENGTH
                            
    def generate_provinces(self) -> None:
        """Генерирует провинции на карте."""
        # Очищаем старые провинции
        self.provinces.clear()
        self.cell_to_province.clear()
        self.province_manager = ProvinceManager()
        
        # Собираем все клетки суши
        land_cells = set()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1:
                    land_cells.add((x, y))
        
        # Создаем провинции пока есть свободные клетки
        while land_cells:
            # Создаем новую провинцию
            province_id = self.province_manager.create_province()
            province_cells = set()
            
            # Выбираем начальную точку провинции
            start = random.choice(list(land_cells))
            province_cells.add(start)
            land_cells.remove(start)
            self.province_manager.add_cell_to_province(province_id, start)
            
            # Расширяем провинцию до нужного размера
            while len(province_cells) < self.province_manager._min_province_size and land_cells:
                candidates = []
                # Находим все соседние клетки
                for cell in province_cells:
                    x, y = cell
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        neighbor = (x + dx, y + dy)
                        if neighbor in land_cells:
                            candidates.append(neighbor)
                
                if not candidates:
                    break
                
                # Выбираем случайную соседнюю клетку
                next_cell = random.choice(candidates)
                province_cells.add(next_cell)
                land_cells.remove(next_cell)
                self.province_manager.add_cell_to_province(province_id, next_cell)
        
        # Обновляем словари для отрисовки
        self.provinces = self.province_manager.provinces
        self.cell_to_province = self.province_manager.cell_to_province


    def get_surface(self) -> pygame.Surface:
        """
        Получает поверхность с отрисованной картой.
        
        Returns:
            pygame.Surface: Поверхность карты
        """
        return self.surface  
          
    def _create_province_entities(self, world: GameWorld) -> None:
        """Создает сущности для провинций."""
        for province_id, cells in self.provinces.items():
            # Создаем сущность провинции
            entity_id = world.create_entity()
            
            # Вычисляем размеры и позицию провинции
            if not cells:  # Пропускаем пустые провинции
                continue
                
            min_x = min(x for x, _ in cells) * TILE_SIZE
            min_y = min(y for _, y in cells) * TILE_SIZE
            max_x = max(x for x, _ in cells) * TILE_SIZE
            max_y = max(y for _, y in cells) * TILE_SIZE
            width = max_x - min_x + TILE_SIZE
            height = max_y - min_y + TILE_SIZE
            
            # Добавляем компонент трансформации
            world.add_component(
                entity_id,
                TransformComponent(
                    x=min_x,
                    y=min_y
                )
            )
            
            # Добавляем компонент отрисовки
            world.add_component(
                entity_id,
                RenderableComponent(
                    color=COLORS['province_neutral'],
                    width=width,
                    height=height,
                    alpha=255,
                    border_width=2,
                    border_color=COLORS['province_border'],
                    layer=RENDER_LAYERS['provinces']  # Используем слой для провинций
                )
            )
            
            # Создаем информацию о провинции
            province_info = ProvinceInfoComponent(f"Province {province_id}")
            cells_copy = cells.copy() if hasattr(cells, 'copy') else set(cells)
            province_info.cells = cells_copy
            world.add_component(entity_id, province_info)
            
            # Добавляем ресурсы
            resource_component = ResourceComponent()
            for x, y in cells:
                resource_type = self.resources.get((x, y))
                if resource_type:
                    resource_component.add_resource(resource_type, 1)
            world.add_component(entity_id, resource_component)