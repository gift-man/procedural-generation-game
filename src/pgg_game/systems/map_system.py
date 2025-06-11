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

from ..world.game_world import GameWorld
from ..components.transform import TransformComponent
from ..components.renderable import RenderableComponent
from ..components.province_info import ProvinceInfoComponent
from ..components.resource import ResourceComponent, ResourceType
from ..config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE,
    GRID_WIDTH, GRID_HEIGHT, COLORS
)

class MapSystem:
    """Система управления картой."""
    
    def __init__(self):
        """Инициализация системы карты."""
        self.grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=np.int32)
        self.provinces: Dict[int, Set[Tuple[int, int]]] = {}
        self.resources: Dict[Tuple[int, int], ResourceType] = {}
        self.world: Optional[GameWorld] = None
        self.map_generated = False
        
        # Настройки генерации
        self.min_province_size = 4
        self.max_province_size = 8
        self.min_island_size = 40
        self.max_island_size = 80
        
        # Настройки ресурсов
        self.resource_clusters = {
            ResourceType.GOLD: {'min_size': 1, 'chance': 0.15},   # Было GOLD_MINE
            ResourceType.STONE: {'min_size': 2, 'chance': 0.25},
            ResourceType.WOOD: {'min_size': 4, 'chance': 0.35},
            ResourceType.FOOD: {'min_size': 1, 'chance': 1.0}     # Луга
        }
        
        # Создаем поверхность для карты
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

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
        self._generate_provinces()
        
        # 4. Генерируем ресурсы
        self._generate_resources()
        
        # 5. Создаем сущности для провинций
        self._create_province_entities(world)
    
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
    
    def _generate_provinces(self) -> None:
        """Разделяет сушу на провинции."""
        province_id = 1
        
        # Проходим по всем клеткам суши
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1 and not any(
                    (x, y) in province 
                    for province in self.provinces.values()
                ):
                    # Создаем новую провинцию
                    province_cells = self._grow_province(x, y)
                    if len(province_cells) >= self.min_province_size:
                        self.provinces[province_id] = province_cells
                        province_id += 1
    
    def _grow_province(self, start_x: int, start_y: int) -> Set[Tuple[int, int]]:
        """Выращивает провинцию из начальной точки."""
        cells = {(start_x, start_y)}
        frontier = [(start_x, start_y)]
        
        while frontier and len(cells) < self.max_province_size:
            x, y = frontier.pop(0)
            
            # Проверяем соседние клетки
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                
                if (0 <= new_x < GRID_WIDTH and 
                    0 <= new_y < GRID_HEIGHT and
                    self.grid[new_y, new_x] == 1 and
                    (new_x, new_y) not in cells and
                    not any((new_x, new_y) in province 
                           for province in self.provinces.values())):
                    cells.add((new_x, new_y))
                    frontier.append((new_x, new_y))
        
        return cells
    
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
    
    def render(self, world: GameWorld) -> None:
        """
        Отрисовка карты.
        
        Args:
            world: Игровой мир
        """
        # Очищаем поверхность
        self.surface.fill(COLORS['water'])  # Заполняем все водой
        
        # 1. Сначала рисуем все клетки и их базовую сетку
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                
                if self.grid[y, x] == 1:  # Если это суша
                    # Получаем тип ресурса для клетки
                    resource_type = self.resources.get((x, y))
                    
                    # Определяем основной цвет клетки и цвет её сетки
                    if resource_type:
                        # Получаем цвета из конфига на основе типа ресурса
                        resource_name = resource_type.value  # получаем строковое значение из enum (wood, gold, stone, food)
                        base_color = COLORS[resource_name]
                        grid_color = COLORS[f'{resource_name}_grid']
                    else:  # По умолчанию - луга (FOOD)
                        base_color = COLORS['food']
                        grid_color = COLORS['food_grid']
                        
                    
                    # Рисуем клетку
                    pygame.draw.rect(self.surface, base_color, rect)
                    # Рисуем сетку клетки
                    pygame.draw.rect(self.surface, grid_color, rect, 1)
                else:  # Если это вода
                    # Рисуем сетку воды
                    pygame.draw.rect(self.surface, COLORS['water_grid'], rect, 1)
        
        # 2. Затем рисуем границу острова
        # Проходим по всем клеткам и ищем границу между сушей и водой
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1:  # Если это суша
                    # Проверяем соседние клетки
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                        new_x, new_y = x + dx, y + dy
                        # Если сосед - вода или за пределами карты
                        if (new_x < 0 or new_x >= GRID_WIDTH or 
                            new_y < 0 or new_y >= GRID_HEIGHT or 
                            self.grid[new_y, new_x] == 0):
                            # Рисуем часть границы острова
                            start_pos = (x * TILE_SIZE, y * TILE_SIZE)
                            if dx == 0 and dy == 1:  # Нижняя граница
                                pygame.draw.line(self.surface, (0, 0, 0), 
                                            (start_pos[0], start_pos[1] + TILE_SIZE),
                                            (start_pos[0] + TILE_SIZE, start_pos[1] + TILE_SIZE), 3)
                            elif dx == 0 and dy == -1:  # Верхняя граница
                                pygame.draw.line(self.surface, (0, 0, 0),
                                            start_pos,
                                            (start_pos[0] + TILE_SIZE, start_pos[1]), 3)
                            elif dx == 1 and dy == 0:  # Правая граница
                                pygame.draw.line(self.surface, (0, 0, 0),
                                            (start_pos[0] + TILE_SIZE, start_pos[1]),
                                            (start_pos[0] + TILE_SIZE, start_pos[1] + TILE_SIZE), 3)
                            elif dx == -1 and dy == 0:  # Левая граница
                                pygame.draw.line(self.surface, (0, 0, 0),
                                            start_pos,
                                            (start_pos[0], start_pos[1] + TILE_SIZE), 3)

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
                    border_width=2,
                    border_color=COLORS['grid_lines']
                )
            )
            
            # Создаем информацию о провинции
            province_info = ProvinceInfoComponent(f"Province {province_id}")
            province_info.cells = cells
            world.add_component(entity_id, province_info)
            
            # Добавляем ресурсы
            resource_component = ResourceComponent()
            for x, y in cells:
                resource_type = self.resources.get((x, y))
                if resource_type:
                    resource_component.add_resource(resource_type, 1)
            world.add_component(entity_id, resource_component)