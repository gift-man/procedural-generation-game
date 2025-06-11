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
        
        # Создаем поверхность для карты
        self.surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
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
            ResourceType.FOOD: {'min_size': 1, 'chance': 1.0}  # Луга
        }

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
        self.surface.fill(COLORS['background'])
        
        # Отрисовываем сетку
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * TILE_SIZE,
                    y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                
                # Определяем цвет клетки
                if self.grid[y, x] == 1:
                    # Суша
                    color = COLORS['land']
                else:
                    # Вода
                    color = COLORS['water']
                
                # Отрисовываем клетку
                pygame.draw.rect(self.surface, color, rect)
                pygame.draw.rect(self.surface, COLORS['grid_lines'], rect, 1)
        
        # Отрисовываем провинции
        for province_id, cells in self.provinces.items():
            # Получаем сущность провинции
            province_entities = [
                (entity_id, world.get_component(entity_id, ProvinceInfoComponent))
                for entity_id in world.get_entities_with_component(ProvinceInfoComponent)
            ]
            
            for entity_id, province_info in province_entities:
                if province_info and province_info.cells == cells:
                    transform = world.get_component(entity_id, TransformComponent)
                    renderable = world.get_component(entity_id, RenderableComponent)
                    
                    if transform and renderable:
                        # Отрисовываем каждую клетку провинции
                        for cell_x, cell_y in cells:
                            rect = pygame.Rect(
                                cell_x * TILE_SIZE,
                                cell_y * TILE_SIZE,
                                TILE_SIZE,
                                TILE_SIZE
                            )
                            
                            # Заливка провинции
                            pygame.draw.rect(
                                self.surface,
                                renderable.color + (100,),  # Полупрозрачный цвет
                                rect
                            )
        
        # Отрисовываем ресурсы
        for (x, y), resource_type in self.resources.items():
            rect = pygame.Rect(
                x * TILE_SIZE + TILE_SIZE // 4,
                y * TILE_SIZE + TILE_SIZE // 4,
                TILE_SIZE // 2,
                TILE_SIZE // 2
            )
            
            # Определяем цвет ресурса
            resource_colors = {
                ResourceType.GOLD: COLORS['gold'],
                ResourceType.STONE: COLORS['stone'],
                ResourceType.WOOD: COLORS['wood'],
                ResourceType.FOOD: COLORS['food']
            }
            
            color = resource_colors.get(resource_type, COLORS['text'])
            
            # Отрисовываем индикатор ресурса
            pygame.draw.circle(
                self.surface,
                color,
                rect.center,
                TILE_SIZE // 4
            )

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