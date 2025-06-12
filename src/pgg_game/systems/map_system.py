"""
Система генерации и управления игровой картой.
"""
import random
from typing import List, Set, Tuple, Dict, Optional
from collections import deque  # Добавляем импорт deque
import pygame
import sys

try:
    import numpy as np
except ImportError:
    print("\nОШИБКА: Библиотека numpy не установлена!")
    print("Для установки выполните команду:")
    print("pip install numpy>=1.24.0")
    sys.exit(1)

from ..world.generators.province_settings import ProvinceGenerationConfig
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

        # 3. Отрисовка границы острова
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Проверяем только клетки суши
                if self.grid[y, x] == 1:
                    # Проверяем все 4 стороны клетки
                    sides = [
                        # формат: (dx, dy, start_pos, end_pos) для каждой стороны
                        # dx, dy - смещение для проверки соседа
                        # start_pos, end_pos - координаты линии границы
                        
                        # Верхняя сторона
                        (0, -1,
                        (x * TILE_SIZE, y * TILE_SIZE),
                        ((x + 1) * TILE_SIZE, y * TILE_SIZE)),
                        
                        # Правая сторона
                        (1, 0,
                        ((x + 1) * TILE_SIZE, y * TILE_SIZE),
                        ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE)),
                        
                        # Нижняя сторона
                        (0, 1,
                        (x * TILE_SIZE, (y + 1) * TILE_SIZE),
                        ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE)),
                        
                        # Левая сторона
                        (-1, 0,
                        (x * TILE_SIZE, y * TILE_SIZE),
                        (x * TILE_SIZE, (y + 1) * TILE_SIZE))
                    ]
                    
                    # Проверяем каждую сторону
                    for dx, dy, start_pos, end_pos in sides:
                        nx, ny = x + dx, y + dy
                        
                        # Если сосед - вода или за пределами карты
                        if (nx < 0 or nx >= GRID_WIDTH or 
                            ny < 0 or ny >= GRID_HEIGHT or 
                            self.grid[ny, nx] == 0):
                            # Рисуем границу острова
                            pygame.draw.line(
                                self.surface,
                                COLORS['border_thick'],
                                start_pos,
                                end_pos,
                                BORDER_THICKNESS
                            )

        # 4. Отрисовка границ провинций
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Проверяем только клетки суши
                if self.grid[y, x] == 1:
                    current_province = self.cell_to_province.get((x, y))
                    if current_province is not None:
                        # Проверяем правую и нижнюю границы
                        neighbors = [
                            # (dx, dy, start_pos, end_pos)
                            # Правая граница
                            (1, 0,
                            ((x + 1) * TILE_SIZE, y * TILE_SIZE),
                            ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE)),
                            
                            # Нижняя граница
                            (0, 1,
                            (x * TILE_SIZE, (y + 1) * TILE_SIZE),
                            ((x + 1) * TILE_SIZE, (y + 1) * TILE_SIZE))
                        ]
                        
                        for dx, dy, start_pos, end_pos in neighbors:
                            nx, ny = x + dx, y + dy
                            
                            # Проверяем соседнюю клетку
                            if (0 <= nx < GRID_WIDTH and 
                                0 <= ny < GRID_HEIGHT and 
                                self.grid[ny, nx] == 1):  # Если сосед - суша
                                
                                neighbor_province = self.cell_to_province.get((nx, ny))
                                
                                # Если провинции разные
                                if (neighbor_province is not None and 
                                    neighbor_province != current_province):
                                    
                                    # Рисуем пунктирную границу
                                    dash_start = start_pos
                                    total_length = (
                                        (end_pos[0] - start_pos[0])**2 + 
                                        (end_pos[1] - start_pos[1])**2
                                    )**0.5
                                    
                                    dash_length = PROVINCE_BORDER_DASH_LENGTH
                                    gap_length = PROVINCE_BORDER_GAP_LENGTH
                                    dash_vector = (
                                        (end_pos[0] - start_pos[0]) / total_length,
                                        (end_pos[1] - start_pos[1]) / total_length
                                    )
                                    
                                    current_pos = 0
                                    while current_pos < total_length:
                                        # Определяем конец текущего штриха
                                        current_end = min(
                                            current_pos + dash_length,
                                            total_length
                                        )
                                        
                                        # Рассчитываем координаты штриха
                                        dash_end = (
                                            start_pos[0] + dash_vector[0] * current_end,
                                            start_pos[1] + dash_vector[1] * current_end
                                        )
                                        dash_start = (
                                            start_pos[0] + dash_vector[0] * current_pos,
                                            start_pos[1] + dash_vector[1] * current_pos
                                        )
                                        
                                        # Рисуем штрих
                                        pygame.draw.line(
                                            self.surface,
                                            COLORS['province_border'],
                                            dash_start,
                                            dash_end,
                                            PROVINCE_BORDER_THICKNESS
                                        )
                                        
                                        # Переходим к следующему штриху
                                        current_pos += dash_length + gap_length
                            
    def generate_provinces(self) -> bool:
        """
        Генерирует провинции на карте.
        
        Returns:
            bool: True если генерация успешна
        """
        config = ProvinceGenerationConfig()
        
        for attempt in range(config.max_generation_attempts):
            print(f"Попытка генерации провинций {attempt + 1}/{config.max_generation_attempts}")
            
            if self._try_generate_provinces(config):
                print("Генерация провинций успешна!")
                return True
                
        print("Не удалось сгенерировать корректные провинции")
        return False

    def _try_generate_provinces(self, config: ProvinceGenerationConfig) -> bool:
        """
        Пытается сгенерировать провинции с заданной конфигурацией.
        
        Args:
            config: Настройки генерации
            
        Returns:
            bool: True если генерация успешна
        """
        # Очищаем старые провинции
        self.provinces.clear()
        self.cell_to_province.clear()
        self.province_manager = ProvinceManager(config=config)
        
        # Собираем все клетки суши
        land_cells = set()
        total_land = 0
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1:
                    land_cells.add((x, y))
                    total_land += 1
                    
        initial_land_count = len(land_cells)
        
        # Основной цикл генерации провинций
        while land_cells:
            if not self._try_create_province(land_cells, config):
                return False
                
            # Проверяем критерии качества
            if len(land_cells) / initial_land_count < (1 - config.min_total_coverage):
                if len(self.province_manager.provinces) >= config.min_province_count:
                    break
                    
        # Финальная проверка качества
        return self._verify_generation_quality(config)

    def _try_create_province(self, land_cells: Set[Tuple[int, int]], 
                            config: ProvinceGenerationConfig) -> bool:
        """
        Пытается создать одну провинцию.
        
        Args:
            land_cells: Доступные клетки суши
            config: Настройки генерации
            
        Returns:
            bool: True если провинция создана успешно
        """
        target_size = self.province_manager.get_ideal_province_size()
        
        for _ in range(config.max_province_attempts):
            # Создаем новую провинцию
            province_id = self.province_manager.create_province(target_size)
            
            # Выбираем стартовую точку с наибольшим количеством соседей
            best_start = self._find_best_start_point(land_cells)
            if not best_start:
                return False
                
            # Пытаемся вырастить провинцию
            if self._grow_province(province_id, best_start, target_size, land_cells):
                return True
                
        return False

    def _find_best_start_point(self, land_cells: Set[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """
        Находит лучшую стартовую точку для новой провинции.
        
        Args:
            land_cells: Доступные клетки суши
            
        Returns:
            Optional[Tuple[int, int]]: Координаты лучшей стартовой точки или None
        """
        best_start = None
        best_score = -1
        
        for cell in land_cells:
            x, y = cell
            # Считаем количество соседей и проверяем возможность плюсового пересечения
            neighbor_count = 0
            has_plus = False
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in land_cells:
                    neighbor_count += 1
                    
                # Проверяем на потенциальное создание плюса
                if (nx, ny) in self.province_manager.cell_to_province:
                    opposite_x = x - dx
                    opposite_y = y - dy
                    if (opposite_x, opposite_y) in self.province_manager.cell_to_province:
                        side_x = x + dy
                        side_y = y - dx
                        if (side_x, side_y) in self.province_manager.cell_to_province:
                            has_plus = True
                            break
            
            if not has_plus and neighbor_count > best_score:
                best_score = neighbor_count
                best_start = cell
                
        return best_start

    def _grow_province(self, province_id: int, start: Tuple[int, int], 
                    target_size: int, land_cells: Set[Tuple[int, int]]) -> bool:
        """
        Выращивает провинцию из стартовой точки.
        
        Args:
            province_id: ID провинции
            start: Стартовая точка
            target_size: Целевой размер провинции
            land_cells: Доступные клетки суши
            
        Returns:
            bool: True если провинция выращена успешно
        """
        # Добавляем стартовую клетку
        if not self.province_manager.add_cell_to_province(province_id, start):
            return False
            
        land_cells.remove(start)
        current_size = 1
        
        # Расширяем провинцию до целевого размера
        while current_size < target_size and land_cells:
            candidates = []
            province_cells = self.province_manager.provinces[province_id].cells
            
            # Собираем все возможные соседние клетки
            for cell in province_cells:
                x, y = cell
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    neighbor = (x + dx, y + dy)
                    if neighbor in land_cells:
                        # Проверяем, не создаст ли добавление клетки плюс
                        if not self.province_manager._would_create_plus_intersection(province_id, neighbor):
                            candidates.append(neighbor)
            
            if not candidates:
                # Если нет подходящих кандидатов и размер слишком мал - считаем провинцию неудачной
                if current_size < self.province_manager.config.min_province_size:
                    return False
                break
                
            # Выбираем лучшего кандидата (с наибольшим числом соседей из этой же провинции)
            best_candidate = None
            best_score = -1
            
            for candidate in candidates:
                x, y = candidate
                score = 0
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if (x + dx, y + dy) in province_cells:
                        score += 1
                if score > best_score:
                    best_score = best_score
                    best_candidate = candidate
                    
            # Добавляем лучшего кандидата
            if best_candidate and self.province_manager.add_cell_to_province(province_id, best_candidate):
                land_cells.remove(best_candidate)
                current_size += 1
            else:
                break
                
        return current_size >= self.province_manager.config.min_province_size

    def _verify_generation_quality(self, config: ProvinceGenerationConfig) -> bool:
        """
        Проверяет качество сгенерированных провинций.
        
        Args:
            config: Настройки генерации
            
        Returns:
            bool: True если качество приемлемо
        """
        # Проверяем количество провинций
        if len(self.province_manager.provinces) < config.min_province_count:
            return False
            
        # Проверяем размеры провинций
        for province in self.province_manager.provinces.values():
            if len(province.cells) < config.min_province_size:
                return False
            if len(province.cells) > config.max_province_size:
                return False
                
        # Проверяем связность провинций
        for province_id, province in self.province_manager.provinces.items():
            if not self._check_province_connectivity(province_id):
                return False
                
        # Проверяем отсутствие плюсовых пересечений
        if config.check_plus_intersection:
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    cell = (x, y)
                    if cell in self.province_manager.cell_to_province:
                        province_id = self.province_manager.cell_to_province[cell]
                        if self.province_manager._would_create_plus_intersection(province_id, cell):
                            return False
                            
        return True

    def _check_province_connectivity(self, province_id: int) -> bool:
        """
        Проверяет связность провинции.
        
        Args:
            province_id: ID провинции
            
        Returns:
            bool: True если провинция связна
        """
        province = self.province_manager.provinces[province_id]
        if not province.cells:
            return True
            
        # Начинаем с первой клетки
        start = next(iter(province.cells))
        visited = {start}
        queue = deque([start])
        
        # Обход в ширину
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if (neighbor in province.cells and 
                    neighbor not in visited):
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        # Все клетки должны быть достижимы
        return len(visited) == len(province.cells)


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