"""
Модуль генерации игровой карты с использованием процедурной генерации.
"""
import random
import pygame
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass
import numpy
import math
from typing import List, Tuple, Optional
from ..world.province_manager import ProvinceManager
from .noise_generator import NoiseConfig, create_noise_generator
from ..world.game_world import GameWorld
from ..components.transform import TransformComponent
from ..components.renderable import RenderableComponent, ShapeType
from ..components.province_info import ProvinceInfoComponent
from ..components.resource import ResourceComponent, ResourceType
from ..config import COLORS, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT
from ..components.province import Province  # Добавляем импорт класса Province

@dataclass
class TerrainConfig:
    """Конфигурация параметров местности."""
    water_level: float = 0.3
    plains_level: float = 0.5
    hills_level: float = 0.7
    mountains_level: float = 0.85
    forest_chance: float = 0.3
    smooth_passes: int = 2

class TerrainType:
    """Типы местности."""
    WATER = "water"
    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAINS = "mountains"
    HILLS = "hills"

    @staticmethod
    def get_color(terrain_type: str) -> pygame.Color:
        """Возвращает цвет для типа местности."""
        colors = {
            TerrainType.WATER: pygame.Color(63, 127, 191),      # Синий
            TerrainType.PLAINS: pygame.Color(127, 191, 63),     # Зеленый
            TerrainType.FOREST: pygame.Color(63, 127, 63),      # Темно-зеленый
            TerrainType.HILLS: pygame.Color(191, 127, 63),      # Коричневый
            TerrainType.MOUNTAINS: pygame.Color(127, 127, 127)  # Серый
        }
        return colors.get(terrain_type, COLORS['province_neutral'])

class MapGenerator:
    """Генератор карты мира."""
    
    def __init__(
        self,
        noise_config: Optional[NoiseConfig] = None,
        terrain_config: Optional[TerrainConfig] = None
    ):
        """
        Инициализирует генератор карты.
        
        Args:
            noise_config: Конфигурация генерации шума
            terrain_config: Конфигурация параметров местности
        """
        self.noise_config = noise_config or NoiseConfig()
        self.terrain_config = terrain_config or TerrainConfig()
        self.noise_gen = create_noise_generator(self.noise_config)
        
        self.province_grid: List[List[int]] = []
        self.terrain_grid: List[List[str]] = []
        
        # Ресурсы для разных типов местности
        self.terrain_resources = {
            TerrainType.PLAINS: {
                ResourceType.FOOD: (5, 10),
                ResourceType.GOLD: (1, 3)
            },
            TerrainType.FOREST: {
                ResourceType.WOOD: (8, 12),
                ResourceType.FOOD: (3, 6)
            },
            TerrainType.MOUNTAINS: {
                ResourceType.STONE: (8, 12),
                ResourceType.IRON: (5, 8)
            },
            TerrainType.HILLS: {
                ResourceType.STONE: (4, 7),
                ResourceType.GOLD: (3, 6)
            }
        }

    def generate_map(self, world: GameWorld) -> None:
        """
        Генерирует новую карту мира.
        
        Args:
            world: Игровой мир для размещения сущностей
        """
        print("MapGenerator: Начало генерации карты...")
        
        # Генерируем карту высот
        height_map = self._generate_height_map()
        
        # Инициализируем сетки
        self.province_grid = [[-1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.terrain_grid = [[TerrainType.WATER for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Создаем провинции
        self._create_provinces(world, height_map)
        
        # Сглаживаем границы
        for _ in range(self.terrain_config.smooth_passes):
            self._smooth_terrain()
        
        # Соединяем соседние провинции
        self._connect_provinces(world)
        
        print("MapGenerator: Генерация карты завершена")
    
    def _generate_height_map(self) -> List[List[float]]:
        """
        Генерирует карту высот используя настроенный генератор шума.
        
        Returns:
            List[List[float]]: Карта высот
        """
        height_map = []
        
        for y in range(GRID_HEIGHT):
            row = []
            for x in range(GRID_WIDTH):
                # Преобразуем координаты сетки в координаты шума
                nx = x / GRID_WIDTH
                ny = y / GRID_HEIGHT
                
                # Получаем базовое значение шума
                value = self.noise_gen.noise2d(nx, ny)
                
                # Нормализуем значение от 0 до 1
                value = (value + 1) * 0.5
                
                # Добавляем небольшую случайность
                value += random.uniform(-0.05, 0.05)
                value = max(0.0, min(1.0, value))
                
                row.append(value)
            height_map.append(row)
        
        return height_map
    
    def _determine_terrain_type(self, height: float) -> str:
        """
        Определяет тип местности по высоте.
        
        Args:
            height: Значение высоты (0-1)
            
        Returns:
            str: Тип местности
        """
        if height < self.terrain_config.water_level:
            return TerrainType.WATER
        elif height < self.terrain_config.plains_level:
            return TerrainType.PLAINS
        elif height < self.terrain_config.hills_level:
            if random.random() < self.terrain_config.forest_chance:
                return TerrainType.FOREST
            return TerrainType.PLAINS
        elif height < self.terrain_config.mountains_level:
            return TerrainType.HILLS
        else:
            return TerrainType.MOUNTAINS
    
    def _create_provinces(self, world: GameWorld, height_map: List[List[float]]) -> None:
        """
        Создает провинции на основе карты высот.
        
        Args:
            world: Игровой мир
            height_map: Карта высот
        """
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                height = height_map[y][x]
                terrain_type = self._determine_terrain_type(height)
                
                if terrain_type != TerrainType.WATER:
                    province_id = self._create_province(world, x, y, terrain_type)
                    self.province_grid[y][x] = province_id
                    self.terrain_grid[y][x] = terrain_type
    
    def _create_province(self, world: GameWorld, x: int, y: int, terrain_type: str) -> int:
        """
        Создает новую провинцию.
        
        Args:
            world: Игровой мир
            x: Координата X на сетке
            y: Координата Y на сетке
            terrain_type: Тип местности
            
        Returns:
            int: ID созданной провинции
        """
        province_id = world.create_entity()
        
        # Создаем компоненты провинции
        transform = TransformComponent(
            x=x * TILE_SIZE,
            y=y * TILE_SIZE,
            width=TILE_SIZE - 2,
            height=TILE_SIZE - 2
        )
        
        renderable = RenderableComponent(
            color=TerrainType.get_color(terrain_type),
            shape=ShapeType.RECTANGLE,
            layer=1,
            border_width=1
        )
        
        province_info = ProvinceInfoComponent(
            name=f"P-{x}-{y}",
            resources={}
        )
        
        # Добавляем ресурсы
        resource_component = ResourceComponent()
        if terrain_type in self.terrain_resources:
            for resource_type, (min_amount, max_amount) in self.terrain_resources[terrain_type].items():
                amount = random.randint(min_amount, max_amount)
                resource_component.amounts[resource_type] = amount
                resource_component.production[resource_type] = amount // 2
        
        # Добавляем все компоненты к сущности
        world.add_component(province_id, transform)
        world.add_component(province_id, renderable)
        world.add_component(province_id, province_info)
        world.add_component(province_id, resource_component)
        
        return province_id
    
    def _connect_provinces(self, world: GameWorld) -> None:
        """Устанавливает связи между соседними провинциями."""
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                province_id = self.province_grid[y][x]
                if province_id == -1:
                    continue
                
                province = world.get_component(province_id, ProvinceInfoComponent)
                if not province:
                    continue
                
                # Проверяем соседей
                for dx, dy in directions:
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < GRID_WIDTH and 
                        0 <= new_y < GRID_HEIGHT):
                        neighbor_id = self.province_grid[new_y][new_x]
                        if neighbor_id != -1:
                            province.add_neighbor(neighbor_id)
    
    def _smooth_terrain(self) -> None:
        """Сглаживает границы местности."""
        smoothed = [row[:] for row in self.terrain_grid]
        
        for y in range(1, GRID_HEIGHT - 1):
            for x in range(1, GRID_WIDTH - 1):
                if self.terrain_grid[y][x] == TerrainType.WATER:
                    continue
                
                neighbors = self._get_neighbor_terrains(x, y)
                most_common = max(set(neighbors), key=neighbors.count)
                
                if neighbors.count(most_common) >= 5:
                    smoothed[y][x] = most_common
        
        self.terrain_grid = smoothed
    
    def _get_neighbor_terrains(self, x: int, y: int) -> List[str]:
        """
        Получает типы местности соседних клеток.
        
        Args:
            x: Координата X
            y: Координата Y
            
        Returns:
            List[str]: Список типов местности соседних клеток
        """
        neighbors = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < GRID_WIDTH and 
                    0 <= new_y < GRID_HEIGHT):
                    neighbors.append(self.terrain_grid[new_y][new_x])
        return neighbors
    def check_area_suitable(self, x, y, radius=10):
        """Проверяет, подходит ли область вокруг точки для размещения провинции"""
        land_count = 0
        total_points = 0
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                check_x = x + dx
                check_y = y + dy
                if (0 <= check_x < self.width and 
                    0 <= check_y < self.height):
                    total_points += 1
                    if self.height_map[check_y][check_x] > self.water_level:
                        land_count += 1
        
        # Требуем, чтобы минимум 60% области было сушей
        return (land_count / total_points) > 0.6 if total_points > 0 else False
    def _create_land_mask(self) -> list:
        """Создает маску суши."""
        mask = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                row.append(1 if self._is_land(x, y) else 0)
            mask.append(row)
        return mask

    def _divide_land_into_regions(self, land_mask: list) -> list:
        """
        Разделяет сушу на регионы методом водораздела.
        """
        regions = []
        width = len(land_mask[0])
        height = len(land_mask)
        
        # Создаем сетку потенциальных центров
        grid_size = min(width, height) // int(math.sqrt(self.num_provinces * 2))
        centers = []
        
        for x in range(grid_size // 2, width, grid_size):
            for y in range(grid_size // 2, height, grid_size):
                if land_mask[y][x]:
                    centers.append((x, y))
        
        if len(centers) < self.num_provinces:
            return []
            
        # Выбираем случайные центры из доступных
        random.shuffle(centers)
        selected_centers = centers[:self.num_provinces]
        
        # Создаем регионы методом ближайшего соседа
        region_map = [[-1 for _ in range(width)] for _ in range(height)]
        regions = [[] for _ in range(self.num_provinces)]
        
        # Распределяем точки по регионам
        for y in range(height):
            for x in range(width):
                if land_mask[y][x]:
                    # Находим ближайший центр
                    min_dist = float('inf')
                    closest_region = -1
                    
                    for i, (cx, cy) in enumerate(selected_centers):
                        dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                        if dist < min_dist:
                            min_dist = dist
                            closest_region = i
                    
                    if closest_region != -1:
                        region_map[y][x] = closest_region
                        regions[closest_region].append((x, y))
        
        # Сглаживаем границы регионов
        self._smooth_regions(region_map, land_mask)
        
        return regions

    def _smooth_regions(self, region_map: list, land_mask: list, iterations: int = 2):
        """Сглаживает границы регионов."""
        width = len(region_map[0])
        height = len(region_map)
        
        for _ in range(iterations):
            new_map = [row[:] for row in region_map]
            
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    if land_mask[y][x]:
                        # Подсчитываем преобладающий регион среди соседей
                        neighbors = {}
                        for dy in [-1, 0, 1]:
                            for dx in [-1, 0, 1]:
                                if dx == 0 and dy == 0:
                                    continue
                                neighbor_region = region_map[y + dy][x + dx]
                                if neighbor_region != -1:
                                    neighbors[neighbor_region] = neighbors.get(neighbor_region, 0) + 1
                        
                        if neighbors:
                            most_common = max(neighbors.items(), key=lambda x: x[1])[0]
                            new_map[y][x] = most_common
            
            region_map = new_map

    def _find_region_center(self, region: list) -> tuple:
        """Находит центр масс региона."""
        if not region:
            return (0, 0)
            
        sum_x = sum(x for x, y in region)
        sum_y = sum(y for x, y in region)
        center_x = sum_x // len(region)
        center_y = sum_y // len(region)
        
        # Находим ближайшую точку суши к центру масс
        best_point = region[0]
        min_dist = float('inf')
        
        for x, y in region:
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            if dist < min_dist and self._is_land(x, y):
                min_dist = dist
                best_point = (x, y)
        
        return best_point    
    def _generate_provinces(self) -> bool:
        """
        Новый подход к генерации провинций, основанный на разделении территории.
        """
        # Создаем маску суши
        land_mask = self._create_land_mask()
        if not land_mask:
            return False
            
        # Разделяем сушу на регионы примерно равного размера
        regions = self._divide_land_into_regions(land_mask)
        if len(regions) < self.num_provinces:
            return False
            
        # Создаем провинции из регионов
        for i in range(self.num_provinces):
            if i < len(regions):
                center_x, center_y = self._find_region_center(regions[i])
                province = Province(i, center_x, center_y)
                self.provinces.append(province)
        
        return len(self.provinces) == self.num_provinces

    def get_province_at(self, screen_x: int, screen_y: int) -> int:
        """
        Возвращает ID провинции по координатам экрана.
        
        Args:
            screen_x: Координата X на экране
            screen_y: Координата Y на экране
            
        Returns:
            int: ID провинции или -1 если провинции нет
        """
        grid_x = screen_x // TILE_SIZE
        grid_y = screen_y // TILE_SIZE
        
        if (0 <= grid_x < GRID_WIDTH and 
            0 <= grid_y < GRID_HEIGHT):
            return self.province_grid[grid_y][grid_x]
        return -1