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
    GRID_WIDTH, GRID_HEIGHT, COLORS
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
    
    def _generate_provinces(self) -> None:
        """Разделяет сушу на провинции."""
        # Получаем все клетки суши
        land_cells = set()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1:
                    land_cells.add((x, y))
        
        # Создаем начальные провинции
        while land_cells and len(self.province_manager.provinces) < 20:  # MAX_PROVINCES
            # Находим хорошую начальную точку
            best_start = None
            best_score = -1

            for cell in land_cells:
                x, y = cell
                neighbor_count = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                                if (x + dx, y + dy) in land_cells)
                
                if neighbor_count > best_score:
                    best_score = neighbor_count
                    best_start = cell

            if not best_start:
                break

            # Создаем новую провинцию
            province_id = self.province_manager.create_province()
            if self.province_manager.add_cell_to_province(province_id, best_start):
                land_cells.remove(best_start)

        # Расширяем провинции
        while land_cells:
            grew = False
            
            # Сортируем провинции по размеру (меньшие растут первыми)
            provinces_by_size = sorted(
                self.province_manager.provinces.keys(),
                key=lambda pid: len(self.province_manager.provinces[pid])  # Используем len() на множестве
            )

            for province_id in provinces_by_size:
                province_cells = self.province_manager.provinces[province_id]
                
                # Находим доступные соседние клетки
                candidates = set()
                for cell in province_cells:  # Используем province_cells напрямую
                    x, y = cell
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        neighbor = (x + dx, y + dy)
                        if neighbor in land_cells:
                            candidates.add(neighbor)

                # Пробуем добавить лучшую клетку
                best_cell = None
                best_score = -1

                for cell in candidates:
                    x, y = cell
                    score = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                            if (x + dx, y + dy) in province_cells)  # Используем province_cells
                    
                    if score > best_score:
                        best_score = score
                        best_cell = cell

                if best_cell and self.province_manager.add_cell_to_province(province_id, best_cell):
                    land_cells.remove(best_cell)
                    grew = True

            if not grew:
                break

        # Обновляем наши словари для отрисовки
        self.provinces = self.province_manager.provinces
        self.cell_to_province = self.province_manager.cell_to_province

        # Создаем сущности для провинций
        self._create_province_entities(self.world)
    
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
                        resource_name = resource_type.value
                        base_color = COLORS[resource_name]
                        grid_color = COLORS[f'{resource_name}_grid']
                    else:  # По умолчанию - луга (FOOD)
                        base_color = COLORS['food']
                        grid_color = COLORS['food_grid']
                    
                    # Рисуем клетку
                    pygame.draw.rect(self.surface, base_color, rect)
                    
                    # Если клетка принадлежит провинции, накладываем оттенок цвета провинции
                    if (x, y) in self.cell_to_province:
                        province_id = self.cell_to_province[(x, y)]
                        province_color = self._get_province_color(province_id)
                        overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                        pygame.draw.rect(overlay, (*province_color, 128), overlay.get_rect())
                        self.surface.blit(overlay, rect)
                    
                    # Рисуем сетку клетки
                    pygame.draw.rect(self.surface, grid_color, rect, 1)
                else:  # Если это вода
                    # Рисуем сетку воды
                    pygame.draw.rect(self.surface, COLORS['grid_lines_water'], rect, 1)
        
            # В методе render замените часть с отрисовкой границ провинций на:
        # 2. Рисуем границы провинций
        for province_id, province_cells in self.provinces.items():
            # Получаем граничные клетки провинции
            border_cells = self.province_manager.get_border_cells(province_id)
            
            for cell in border_cells:
                x, y = cell
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                # Проверяем каждую сторону клетки
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    neighbor = (x + dx, y + dy)
                    # Проверяем, принадлежит ли сосед другой провинции или является водой
                    if neighbor not in self.cell_to_province or \
                    self.cell_to_province[neighbor] != province_id:
                        # Рисуем границу провинции
                        if dx == 0:  # Вертикальная граница
                            start_pos = (rect.x + (TILE_SIZE if dx > 0 else 0), rect.y)
                            end_pos = (start_pos[0], rect.y + TILE_SIZE)
                        else:  # Горизонтальная граница
                            start_pos = (rect.x, rect.y + (TILE_SIZE if dy > 0 else 0))
                            end_pos = (rect.x + TILE_SIZE, start_pos[1])
                        
                        pygame.draw.line(self.surface, COLORS['province_border'],
                                    start_pos, end_pos, 2)
        
        # 3. Затем рисуем границу острова
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1:  # Если это суша
                    # Проверяем соседние клетки
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        new_x, new_y = x + dx, y + dy
                        # Если сосед - вода или за пределами карты
                        if (new_x < 0 or new_x >= GRID_WIDTH or 
                            new_y < 0 or new_y >= GRID_HEIGHT or 
                            self.grid[new_y, new_x] == 0):
                            # Рисуем толстую границу острова
                            rect = pygame.Rect(
                                x * TILE_SIZE,
                                y * TILE_SIZE,
                                TILE_SIZE,
                                TILE_SIZE
                            )
                            if dx == 0:  # Вертикальная граница
                                if dy == 1:  # Нижняя
                                    pygame.draw.line(self.surface, COLORS['border_thick'],
                                                (rect.left, rect.bottom),
                                                (rect.right, rect.bottom), 3)
                                else:  # Верхняя
                                    pygame.draw.line(self.surface, COLORS['border_thick'],
                                                (rect.left, rect.top),
                                                (rect.right, rect.top), 3)
                            else:  # Горизонтальная граница
                                if dx == 1:  # Правая
                                    pygame.draw.line(self.surface, COLORS['border_thick'],
                                                (rect.right, rect.top),
                                                (rect.right, rect.bottom), 3)
                                else:  # Левая
                                    pygame.draw.line(self.surface, COLORS['border_thick'],
                                                (rect.left, rect.top),
                                                (rect.left, rect.bottom), 3)
                                
    def generate_provinces(self):
        """Генерирует провинции на карте."""
        # Собираем все клетки суши
        land_cells = set()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1:
                    land_cells.add((x, y))

        # Создаем начальные провинции
        while land_cells and len(self.province_manager.provinces) < 20:  # MAX_PROVINCES
            # Находим хорошую начальную точку
            best_start = None
            best_score = -1

            for cell in land_cells:
                x, y = cell
                neighbor_count = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                                if (x + dx, y + dy) in land_cells)
                
                if neighbor_count > best_score:
                    best_score = neighbor_count
                    best_start = cell

            if not best_start:
                break

            # Создаем новую провинцию
            province_id = self.province_manager.create_province()
            if self.province_manager.add_cell_to_province(province_id, best_start):
                land_cells.remove(best_start)

        # Расширяем провинции
        while land_cells:
            grew = False
            
            # Сортируем провинции по размеру (меньшие растут первыми)
            provinces_by_size = sorted(
                self.province_manager.provinces.keys(),
                key=lambda pid: len(self.province_manager.provinces[pid].cells)
            )

            for province_id in provinces_by_size:
                province = self.province_manager.provinces[province_id]
                
                # Находим доступные соседние клетки
                candidates = set()
                for cell in province.cells:
                    x, y = cell
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        neighbor = (x + dx, y + dy)
                        if neighbor in land_cells:
                            candidates.add(neighbor)

                # Пробуем добавить лучшую клетку
                best_cell = None
                best_score = -1

                for cell in candidates:
                    x, y = cell
                    score = sum(1 for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                            if (x + dx, y + dy) in province.cells)
                    
                    if score > best_score:
                        best_score = score
                        best_cell = cell

                if best_cell and self.province_manager.add_cell_to_province(province_id, best_cell):
                    land_cells.remove(best_cell)
                    grew = True

            if not grew:
                break

        # Обновляем наши словари для отрисовки
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
            
            # Создаем информацию о провинции
            province_info = ProvinceInfoComponent(f"Province {province_id}")
            province_info.cells = cells  # Устанавливаем cells непосредственно из множества
            world.add_component(entity_id, province_info)
            
            # Добавляем ресурсы
            resource_component = ResourceComponent()
            for x, y in cells:
                resource_type = self.resources.get((x, y))
                if resource_type:
                    resource_component.add_resource(resource_type, 1)
            world.add_component(entity_id, resource_component)