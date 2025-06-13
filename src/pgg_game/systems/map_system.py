"""
Система генерации и управления игровой картой.
"""
import random
from typing import List, Set, Tuple, Dict, Optional
from collections import deque  # Добавляем импорт deque
import pygame
import sys
import math

try:
    import numpy as np
except ImportError:
    print("\nОШИБКА: Библиотека numpy не установлена!")
    print("Для установки выполните команду:")
    print("pip install numpy>=1.24.0")
    sys.exit(1)


from ..world.generators.island_analyzer import IslandAnalyzer
from ..world.generators.map_generation_settings import MapGenerationSettings
from ..config import COLORS, RENDER_LAYERS
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
        self.province_manager = None  # Создаём менеджера провинций позже
        
        # Загружаем настройки генерации
        self.generation_settings = MapGenerationSettings()
        
        # Настройки генерации
        self.min_province_size = self.generation_settings.min_province_size
        self.max_province_size = self.generation_settings.max_province_size
        self.min_island_size = self.generation_settings.min_total_size
        self.max_island_size = self.generation_settings.min_total_size * 2
        
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
        """Генерирует новую карту."""
        try:
            max_retries = 5
            for retry in range(max_retries):
                print(f"Попытка генерации {retry + 1}")
                
                # Генерируем остров из провинций
                if self._generate_islands():
                    # Создаем провинции
                    if self._create_province_entities(world):
                        # Генерируем ресурсы
                        self._generate_resources()
                        self.map_generated = True
                        print("Генерация карты успешно завершена")
                        return
                
                print(f"Попытка {retry + 1} не удалась")
                
            raise RuntimeError("Не удалось сгенерировать карту после всех попыток")
            
        except Exception as e:
            print(f"Ошибка при генерации карты: {e}")
            raise

    def _flood_fill(self, start_x: int, start_y: int) -> Set[Tuple[int, int]]:
        """Находит все связанные клетки суши, начиная с заданной точки."""
        cells = set()
        queue = [(start_x, start_y)]
        
        while queue:
            x, y = queue.pop(0)
            if (x, y) in cells:
                continue
                
            if (0 <= x < GRID_WIDTH and 
                0 <= y < GRID_HEIGHT and 
                self.grid[y, x] == 1):
                cells.add((x, y))
                
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    queue.append((x + dx, y + dy))
        
        return cells
    
    def _create_initial_provinces(self, world: GameWorld) -> List[Dict]:
        """Создает начальные провинции на основе сгенерированной карты."""
        provinces = []
        
        # Находим все компоненты связности в сетке (острова)
        visited = set()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y, x] == 1 and (x, y) not in visited:
                    # Нашли новую провинцию
                    province_cells = self._flood_fill(x, y)
                    if len(province_cells) >= 4:  # Минимальный размер провинции
                        visited.update(province_cells)
                        
                        # Создаем сущность провинции
                        province_id = world.create_entity()
                        
                        # Находим центр провинции
                        center_x = sum(x for x, _ in province_cells) // len(province_cells)
                        center_y = sum(y for _, y in province_cells) // len(province_cells)
                        
                        # Создаем компоненты
                        transform = TransformComponent(x=center_x * TILE_SIZE, y=center_y * TILE_SIZE)
                        renderable = RenderableComponent(color=COLORS['province_neutral'])
                        province_info = ProvinceInfoComponent(name=f"P{len(provinces)}")
                        
                        # Добавляем компоненты
                        world.add_component(province_id, transform)
                        world.add_component(province_id, renderable)
                        world.add_component(province_id, province_info)
                        
                        provinces.append({
                            'id': province_id,
                            'cells': province_cells,
                            'center': (center_x, center_y)
                        })
        
        return provinces
    
    def _verify_final_state(self) -> bool:
        """Проверяет финальное состояние карты."""
        if not self.province_manager.provinces:
            return False
            
        # Проверяем базовые требования
        min_provinces = self.province_manager.config.min_province_count
        max_provinces = self.province_manager.config.max_province_count
        if not (min_provinces <= len(self.province_manager.provinces) <= max_provinces):
            return False
        
        # Проверяем размеры провинций
        for province in self.province_manager.provinces.values():
            if not (self.province_manager.config.min_province_size <= 
                    len(province.cells) <= 
                    self.province_manager.config.max_province_size):
                return False
        
        # Проверяем, что все провинции связные
        for province_id in self.province_manager.provinces:
            if not self._check_province_connectivity(province_id):
                return False
        
        # Подсчитываем общее покрытие
        total_land = sum(1 for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) 
                        if self.grid[y, x] == 1)
        if total_land == 0:
            return False
            
        total_province_cells = sum(len(p.cells) for p in self.province_manager.provinces.values())
        coverage = total_province_cells / total_land
        
        return coverage >= self.province_manager.config.min_total_coverage
    
    def _generate_with_timeout(self, timeout: float) -> bool:
        """
        Пытается сгенерировать провинции с таймаутом.
        
        Args:
            timeout: Максимальное время в секундах
        
        Returns:
            bool: True если генерация успешна
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.generate_provinces():
                return True
                
        return False
    
    def _update_province_mapping(self) -> None:
        """Обновляет маппинг клеток к провинциям."""
        self.cell_to_province.clear()
        for province_id, province in self.province_manager.provinces.items():
            for cell in province.cells:
                self.cell_to_province[cell] = province_id

    def _generate_islands(self) -> bool:
        """
        Генерирует остров из провинций.
        
        Returns:
            bool: True если генерация успешна
        """
        config = self.province_manager.config
        
        # 1. Очищаем сетку
        self.grid.fill(0)
        
        # 2. Создаем начальные провинции по кругу от центра
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        provinces = []
        
        # Определяем количество начальных провинций
        province_count = random.randint(config.min_provinces, config.max_provinces)
        
        for i in range(province_count):
            # Размещаем провинции по кругу
            angle = (2 * math.pi * i) / province_count
            radius = config.initial_radius
            
            # Вычисляем позицию
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            
            # Проверяем границы
            x = max(config.edge_distance, min(x, GRID_WIDTH - config.edge_distance))
            y = max(config.edge_distance, min(y, GRID_HEIGHT - config.edge_distance))
            
            # Создаем провинцию
            province = {
                'id': i,
                'center': (x, y),
                'cells': {(x, y)},
                'size': random.randint(config.min_size, config.max_size),
                'grown': False
            }
            
            provinces.append(province)
            self.grid[y, x] = 1
        
        # 3. Растим провинции пошагово
        for _ in range(config.growth_steps):
            # Перемешиваем провинции для случайного порядка роста
            random.shuffle(provinces)
            
            for province in provinces:
                if len(province['cells']) >= province['size']:
                    province['grown'] = True
                    continue
                    
                # Собираем возможные клетки для роста
                candidates = self._get_growth_candidates(province, config)
                if not candidates:
                    continue
                
                # Выбираем лучшие клетки и добавляем их
                best_cells = self._select_best_cells(
                    candidates, 
                    province, 
                    min(3, province['size'] - len(province['cells'])),
                    config
                )
                
                for cell in best_cells:
                    province['cells'].add(cell)
                    self.grid[cell[1], cell[0]] = 1
        
        # 4. Соединяем близкие провинции
        self._connect_provinces(provinces, config)
        
        # 5. Сглаживаем границы
        for _ in range(config.border_smoothing):
            new_grid = self.grid.copy()
            for y in range(1, GRID_HEIGHT - 1):
                for x in range(1, GRID_WIDTH - 1):
                    neighbors = sum(self.grid[y+dy, x+dx] for dx, dy in 
                                [(0, 1), (1, 0), (0, -1), (-1, 0)])
                    if neighbors >= 3:
                        new_grid[y, x] = 1
                    elif neighbors <= 1:
                        new_grid[y, x] = 0
            self.grid = new_grid
        
        # 6. Проверяем результат
        land_count = np.sum(self.grid)
        min_required = config.min_provinces * config.min_size
        return land_count >= min_required
   
    def _get_growth_candidates(self, province: dict, config: ProvinceGenerationConfig) -> set:
        """Находит возможные клетки для роста провинции."""
        candidates = set()
        
        for x, y in province['cells']:
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x = x + dx
                new_y = y + dy
                
                # Проверяем границы и занятость
                if (config.edge_distance <= new_x < GRID_WIDTH - config.edge_distance and
                    config.edge_distance <= new_y < GRID_HEIGHT - config.edge_distance and
                    self.grid[new_y, new_x] == 0):
                    
                    # Проверяем количество соседей
                    neighbors = sum(1 for ddx, ddy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                                if (new_x + ddx, new_y + ddy) in province['cells'])
                    
                    if config.min_neighbors <= neighbors <= config.max_neighbors:
                        candidates.add((new_x, new_y))
        
        return candidates

    def _select_best_cells(self, candidates: set, province: dict, 
                        count: int, config: ProvinceGenerationConfig) -> list:
        """Выбирает лучшие клетки для роста провинции."""
        if not candidates:
            return []
        
        scores = []
        center_x, center_y = province['center']
        
        for x, y in candidates:
            # Считаем соседей
            neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                        if (x + dx, y + dy) in province['cells'])
            
            # Расстояние до центра
            dist = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            center_score = 1.0 / (1.0 + dist)
            
            # Штраф за близость к краю
            edge_dist = min(x, y, GRID_WIDTH - x, GRID_HEIGHT - y)
            edge_score = edge_dist / max(GRID_WIDTH, GRID_HEIGHT)
            
            # Итоговый счет
            score = (neighbors * config.weights['neighbor_count'] +
                    center_score * config.weights['center_distance'] +
                    edge_score * config.weights['edge_penalty'])
                    
            scores.append((score, (x, y)))
        
        # Выбираем лучшие клетки
        scores.sort(reverse=True)
        return [cell for _, cell in scores[:count]]

    def _connect_provinces(self, provinces: list, config: ProvinceGenerationConfig) -> None:
        """Соединяет близкие провинции."""
        for i, p1 in enumerate(provinces[:-1]):
            for p2 in provinces[i+1:]:
                # Ищем ближайшие точки между провинциями
                min_dist = float('inf')
                best_pair = None
                
                for c1 in p1['cells']:
                    for c2 in p2['cells']:
                        dist = ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2) ** 0.5
                        if dist < min_dist:
                            min_dist = dist
                            best_pair = (c1, c2)
                
                # Если провинции достаточно близко, соединяем их
                if min_dist <= config.spacing * 2:
                    self._draw_line(best_pair[0], best_pair[1])

    def _draw_line(self, start: tuple, end: tuple) -> None:
        """Рисует линию между двумя точками, заполняя её единицами."""
        x1, y1 = start
        x2, y2 = end
        
        # Используем алгоритм Брезенхэма для рисования линии
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            self.grid[y, x] = 1
            
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
                
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
        """Генерирует провинции на карте."""
        # Подсчитываем общее количество клеток суши
        land_count = sum(1 for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) 
                        if self.grid[y, x] == 1)
        
        # Проверяем минимальный размер острова
        if land_count < self.min_island_size:
            print(f"Остров слишком мал (нужно {self.min_island_size}, есть {land_count})")
            return False
        
        # Создаем новую конфигурацию с адаптированными параметрами
        config = ProvinceGenerationConfig()
        config.min_province_size = max(4, land_count // 20)  # Не менее 4 клеток
        config.max_province_size = min(8, land_count // 5)   # Не более 20% острова
        
        # Пытаемся сгенерировать провинции
        for attempt in range(config.max_generation_attempts):
            if self._try_generate_provinces(config):
                return True
            print(f"Попытка {attempt + 1}: Не удалось сгенерировать провинции")
        
        return False

    def _try_generate_provinces(self, config: ProvinceGenerationConfig) -> bool:
        """Пытается сгенерировать провинции."""
        # Собираем все клетки суши
        land_cells = {(x, y) for y in range(GRID_HEIGHT) 
                    for x in range(GRID_WIDTH) if self.grid[y, x] == 1}
        
        if not land_cells:
            return False
            
        # Вычисляем оптимальное количество провинций на основе размера острова
        total_land = len(land_cells)
        target_provinces = max(3, min(15, total_land // 6))  # Примерно 6 клеток на провинцию
        
        # Обновляем конфигурацию
        config.max_province_count = target_provinces
        config.min_province_count = max(3, target_provinces - 2)
        
        # Очищаем старые провинции
        self.provinces.clear()
        self.cell_to_province.clear()
        self.province_manager = ProvinceManager(config=config)
        
        # Собираем все клетки суши
        unassigned_cells = land_cells.copy()
        
        # Находим центральную точку острова
        center_x = sum(x for x, _ in land_cells) / len(land_cells)
        center_y = sum(y for _, y in land_cells) / len(land_cells)
        center = (center_x, center_y)
        
        # Основной цикл генерации
        while unassigned_cells:
            # Выбираем стартовую точку
            start = self._find_best_start_point(unassigned_cells, center)
            if not start:
                break
                
            # Определяем размер новой провинции
            remaining_cells = len(unassigned_cells)
            remaining_provinces = target_provinces - len(self.province_manager.provinces)
            
            if remaining_provinces <= 0:
                # Если превысили количество провинций, добавляем оставшиеся клетки к существующим
                self._distribute_remaining_cells(unassigned_cells)
                break
                
            # Вычисляем идеальный размер для оставшихся провинций
            ideal_size = remaining_cells // remaining_provinces
            target_size = min(max(config.min_province_size,
                                ideal_size),
                            config.max_province_size)
            
            # Создаем новую провинцию
            province_id = self.province_manager.create_province()
            
            # Расширяем провинцию
            cells_to_add = self._grow_province_from_center(start, target_size, unassigned_cells)
            
            # Добавляем клетки в провинцию
            for cell in cells_to_add:
                if self.province_manager.add_cell_to_province(province_id, cell):
                    unassigned_cells.remove(cell)
        
        # Проверяем результат
        if unassigned_cells:  # Если остались неназначенные клетки
            return False
            
        if len(self.province_manager.provinces) < config.min_province_count:
            return False
            
        if not self._verify_provinces():
            return False
            
        return True

    
    def _try_create_province(self, land_cells: Set[Tuple[int, int]]) -> bool:
        """Пытается создать одну провинцию."""
        if not land_cells:
            return False
            
        # Создаем новую провинцию
        province_id = self.province_manager.create_province()
        target_size = self.province_manager.get_ideal_province_size()
        
        # Выбираем начальную точку
        start = self._find_best_start_point(land_cells, self.province_manager.config)
        if not start:
            # Если не нашли хорошую точку, удаляем провинцию
            self.province_manager.provinces.pop(province_id, None)
            return False
            
        # Пытаемся вырастить провинцию
        success = self._grow_province(province_id, start, target_size, land_cells)
        if not success:
            # Если не удалось вырастить, удаляем провинцию
            self.province_manager.provinces.pop(province_id, None)
            return False
            
        return True

    
    def _distribute_remaining_cells(self, land_cells: Set[Tuple[int, int]]) -> None:
        """Распределяет оставшиеся клетки по существующим провинциям."""
        while land_cells:
            changes_made = False
            for cell in list(land_cells):  # Создаем копию для итерации
                x, y = cell
                best_province = None
                best_score = float('-inf')
                
                # Ищем лучшую провинцию для клетки
                for province_id, province in self.province_manager.provinces.items():
                    if len(province.cells) >= self.province_manager.config.max_province_size:
                        continue
                    
                    # Считаем количество соседей
                    neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                                if (x + dx, y + dy) in province.cells)
                    
                    if neighbors > 0:  # Только если есть хотя бы один сосед
                        # Оценка учитывает количество соседей и размер провинции
                        score = neighbors - (len(province.cells) / 
                                        self.province_manager.config.max_province_size)
                        
                        if score > best_score:
                            best_score = score
                            best_province = province_id
                
                # Добавляем клетку к лучшей провинции
                if best_province is not None:
                    if self.province_manager.add_cell_to_province(best_province, cell):
                        land_cells.remove(cell)
                        changes_made = True
            
            # Если не удалось распределить ни одну клетку за проход
            if not changes_made:
                break

    def _find_best_start_point(self, land_cells: Set[Tuple[int, int]], 
                            config: ProvinceGenerationConfig) -> Optional[Tuple[int, int]]:
        """
        Находит лучшую стартовую точку для новой провинции.
        """
        best_start = None
        best_score = float('-inf')
        
        # Находим центр масс доступной территории
        if land_cells:
            center_x = sum(x for x, _ in land_cells) / len(land_cells)
            center_y = sum(y for _, y in land_cells) / len(land_cells)
        else:
            return None

        # Находим максимальное расстояние от центра
        max_distance = max(
            ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
            for x, y in land_cells
        ) or 1

        for cell in land_cells:
            x, y = cell
            
            # Проверяем на плюсовые пересечения
            if config.check_plus_intersection:
                has_plus = False
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if self._would_create_plus(x, y, dx, dy):
                        has_plus = True
                        break
                if has_plus:
                    continue

            # Считаем параметры для оценки точки
            neighbor_count = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                            if (x + dx, y + dy) in land_cells)
            
            # Расстояние до центра (нормализованное)
            dist_to_center = (((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5) / max_distance
            
            # Оценка потенциала роста (сколько свободного места вокруг)
            growth_potential = self._evaluate_growth_potential(x, y, land_cells)
            
            # Итоговая оценка точки
            score = (
                neighbor_count * config.weights['neighbor_count'] +
                (1 - dist_to_center) * config.weights['center_distance'] +
                growth_potential * config.weights['compactness']
            )
            
            if score > best_score:
                best_score = score
                best_start = cell
                
        return best_start

    def _evaluate_growth_potential(self, x: int, y: int, 
                                land_cells: Set[Tuple[int, int]], radius: int = 2) -> float:
        """
        Оценивает потенциал роста из данной точки.
        
        Args:
            x: Координата X
            y: Координата Y
            land_cells: Доступные клетки
            radius: Радиус проверки
            
        Returns:
            float: Оценка от 0 до 1
        """
        available = 0
        total = 0
        
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                # Считаем только клетки в пределах "алмаза" (манхэттенское расстояние)
                if abs(dx) + abs(dy) <= radius:
                    total += 1
                    if (x + dx, y + dy) in land_cells:
                        available += 1
                        
        return available / total if total > 0 else 0

    def _would_create_plus(self, x: int, y: int, dx: int, dy: int) -> bool:
        """
        Проверяет, создаст ли добавление клетки плюсовое пересечение.
        """
        opposite_x = x - dx
        opposite_y = y - dy
        side1_x = x + dy
        side1_y = y - dx
        side2_x = x - dy
        side2_y = y + dx
        
        # Проверяем наличие плюсового пересечения
        for check_cell in [(opposite_x, opposite_y), (side1_x, side1_y), (side2_x, side2_y)]:
            if check_cell in self.province_manager.cell_to_province:
                return True
                
        return False
    
    def _evaluate_cell_score(self, cell: Tuple[int, int], province_cells: Set[Tuple[int, int]]) -> float:
        """
        Оценивает пригодность клетки для добавления в провинцию.
        
        Args:
            cell: Оцениваемая клетка (x, y)
            province_cells: Множество клеток текущей провинции
            
        Returns:
            float: Оценка пригодности клетки
        """
        x, y = cell
        
        # Проверяем, что клетка на карте
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return float('-inf')
        
        if self.grid[y, x] != 1:  # Проверяем что это суша
            return float('-inf')
            
        # Подсчёт соседей
        neighbors = 0
        diagonals = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            check_cell = (x + dx, y + dy)
            if check_cell in province_cells:
                if abs(dx) + abs(dy) == 1:  # Прямые соседи
                    neighbors += 1.5  # Увеличиваем вес прямых соседей
                else:  # Диагональные соседи
                    diagonals += 0.5
                    
        neighbor_score = (neighbors + diagonals) / 6.0  # Нормализация
        
        # Вычисляем центр провинции и расстояние до него
        if province_cells:
            center_x = sum(x for x, _ in province_cells) / len(province_cells)
            center_y = sum(y for _, y in province_cells) / len(province_cells)
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx * dx + dy * dy)
            distance_score = 1.0 / (1.0 + distance)  # Нормализованное расстояние
        else:
            distance_score = 1.0
            
        # Проверка компактности (количество пустых клеток вокруг)
        empty_adjacent = 0
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            check_x, check_y = x + dx, y + dy
            if (0 <= check_x < GRID_WIDTH and 
                0 <= check_y < GRID_HEIGHT and 
                self.grid[check_y, check_x] == 1 and
                (check_x, check_y) not in province_cells):
                empty_adjacent += 1
                
        compactness_score = 1.0 - (empty_adjacent / 4.0)  # Нормализация
        
        # Итоговая оценка с весами из конфигурации
        weights = self.province_manager.config.weights
        return (
            neighbor_score * weights['neighbor_count'] +
            distance_score * weights['center_distance'] +
            compactness_score * weights['compactness']
        )
    
    def _cleanup_failed_provinces(self) -> None:
        """Очищает неудачные провинции."""
        to_remove = []
        for province_id, province in self.province_manager.provinces.items():
            # Проверяем размер провинции
            if len(province.cells) < self.province_manager.config.min_province_size:
                to_remove.append(province_id)
                continue
                
            # Проверяем связность провинции
            if not self._check_province_connectivity(province_id):
                to_remove.append(province_id)
                continue
                
        # Удаляем неудачные провинции
        for province_id in to_remove:
            self.province_manager.provinces.pop(province_id)

    def _grow_province(self, province_id: int, start: Tuple[int, int], 
                    target_size: int, land_cells: Set[Tuple[int, int]]) -> bool:
        """Выращивает провинцию из начальной точки."""
        # Пробуем добавить начальную клетку
        if not self.province_manager.add_cell_to_province(province_id, start):
            return False
            
        land_cells.remove(start)
        current_size = 1
        failed_attempts = 0
        max_failed_attempts = 10
        
        # Расширяем провинцию до целевого размера
        while current_size < target_size and land_cells and failed_attempts < max_failed_attempts:
            added_cell = False
            candidates = []
            
            # Собираем всех возможных соседей
            for cell in self.province_manager.provinces[province_id].cells:
                x, y = cell
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    neighbor = (x + dx, y + dy)
                    if neighbor in land_cells:
                        score = self._evaluate_cell_score(neighbor, self.province_manager.provinces[province_id].cells)
                        candidates.append((neighbor, score))
            
            # Если есть кандидаты, выбираем лучшего
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                for next_cell, _ in candidates[:3]:  # Пробуем топ-3 кандидатов
                    if self.province_manager.add_cell_to_province(province_id, next_cell):
                        land_cells.remove(next_cell)
                        current_size += 1
                        added_cell = True
                        break
            
            if not added_cell:
                failed_attempts += 1
                
        return current_size >= self.province_manager.config.min_province_size

    def _calculate_cell_weight(self, x: int, y: int, center_x: float, center_y: float,
                            province_cells: Set[Tuple[int, int]], 
                            land_cells: Set[Tuple[int, int]]) -> float:
        """
        Вычисляет вес клетки для выбора следующей клетки роста.
        """
        # Количество соседей из этой же провинции
        province_neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                            if (x + dx, y + dy) in province_cells)
        
        # Расстояние до центра провинции
        distance_to_center = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
        
        # Потенциал роста
        growth_potential = self._evaluate_cell_score(x, y, land_cells)
        
        # Количество свободных соседей
        free_neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                            if (x + dx, y + dy) in land_cells)
        
        # Нормализуем компоненты
        province_neighbors_norm = province_neighbors / 4
        distance_norm = 1 / (1 + distance_to_center)  # Ближе к центру = лучше
        growth_potential_norm = growth_potential
        free_neighbors_norm = free_neighbors / 4
        
        # Считаем общий вес
        weights = self.province_manager.config.weights
        return (
            province_neighbors_norm * weights['neighbor_count'] +
            distance_norm * weights['center_distance'] +
            growth_potential_norm * weights['compactness'] +
            free_neighbors_norm * weights['border_length']
        )

    def _verify_generation_quality(self, config: ProvinceGenerationConfig) -> bool:
        """
        Проверяет качество сгенерированных провинций.
        
        Args:
            config: Настройки генерации
            
        Returns:
            bool: True если качество приемлемо
        """
        # Проверяем количество провинций
        if len(self.province_manager.provinces) < config.min_province_count:  # Изменено с min_province_count
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
        if not hasattr(self, 'province_manager'):
            return
            
        # Получаем список провинций
        provinces = self.province_manager.get_provinces()
        
        for province in provinces:
            if not province.cells:  # Пропускаем пустые провинции
                continue
                
            # Вычисляем размеры и позицию провинции
            min_x = min(x for x, _ in province.cells)
            min_y = min(y for _, y in province.cells)
            max_x = max(x for x, _ in province.cells)
            max_y = max(y for _, y in province.cells)
            width = max_x - min_x + 1
            height = max_y - min_y + 1
            
            # Создаем сущность провинции
            entity_id = world.create_entity()
            
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
                    layer=RENDER_LAYERS['provinces']
                )
            )
            
            # Создаем информацию о провинции
            province_info = ProvinceInfoComponent(f"Province {province.id}")
            province_info.cells = set(province.cells)  # Создаем копию множества клеток
            world.add_component(entity_id, province_info)

    def _find_best_start_point(self, available_cells: Set[Tuple[int, int]], 
                            center: Tuple[float, float]) -> Optional[Tuple[int, int]]:
        """Находит лучшую стартовую точку для новой провинции."""
        if not available_cells:
            return None
            
        best_point = None
        best_score = float('-inf')
        cx, cy = center
        
        for x, y in available_cells:
            # Оцениваем позицию
            # 1. Расстояние до центра (ближе = лучше)
            dist_score = -((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            
            # 2. Количество доступных соседей
            neighbors = sum(1 for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                        if (x + dx, y + dy) in available_cells)
            neighbor_score = neighbors * 2  # Даем больший вес наличию соседей
            
            # Общая оценка
            score = dist_score + neighbor_score
            
            if score > best_score:
                best_score = score
                best_point = (x, y)
                
        return best_point

    def _grow_province_from_center(self, start: Tuple[int, int], target_size: int,
                                available_cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Выращивает провинцию из начальной точки."""
        province_cells = {start}
        frontier = {start}
        
        while len(province_cells) < target_size and frontier:
            best_cell = None
            best_score = float('-inf')
            
            # Оцениваем все возможные клетки для добавления
            for cell in frontier:
                x, y = cell
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    neighbor = (x + dx, y + dy)
                    if neighbor not in available_cells:
                        continue
                    if neighbor in province_cells:
                        continue
                        
                    # Считаем количество соседей из провинции
                    province_neighbors = sum(
                        1 for ndx, ndy in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                        if (neighbor[0] + ndx, neighbor[1] + ndy) in province_cells
                    )
                    
                    # Оцениваем компактность
                    cx = sum(x for x, _ in province_cells) / len(province_cells)
                    cy = sum(y for _, y in province_cells) / len(province_cells)
                    distance = ((neighbor[0] - cx) ** 2 + (neighbor[1] - cy) ** 2) ** 0.5
                    
                    # Общая оценка
                    score = province_neighbors - (distance * 0.5)
                    
                    if score > best_score:
                        best_score = score
                        best_cell = neighbor
            
            if best_cell is None:
                break
                
            # Добавляем лучшую клетку
            province_cells.add(best_cell)
            frontier.add(best_cell)
            # Удаляем использованные клетки из фронтира
            frontier = {cell for cell in frontier
                    if any((cell[0] + dx, cell[1] + dy) not in province_cells
                            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)])}
        
        return province_cells

    def _verify_provinces(self) -> bool:
        """Проверяет корректность всех провинций."""
        for province in self.province_manager.provinces.values():
            # Проверка размера
            if not (self.province_manager.config.min_province_size <= 
                    len(province.cells) <= 
                    self.province_manager.config.max_province_size):
                return False
                
            # Проверка связности
            start = next(iter(province.cells))
            connected = self._get_connected_cells(start, province.cells)
            if len(connected) != len(province.cells):
                return False
                
            # Проверка соседей (каждая клетка должна иметь хотя бы одного соседа)
            for x, y in province.cells:
                has_neighbor = False
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if (x + dx, y + dy) in province.cells:
                        has_neighbor = True
                        break
                if not has_neighbor:
                    return False
        
        return True         
    def _get_connected_cells(self, start: Tuple[int, int], cells: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """
        Возвращает все связанные клетки из данного множества, начиная с заданной.
        
        Args:
            start: Начальная клетка (x, y)
            cells: Множество всех клеток
            
        Returns:
            Set[Tuple[int, int]]: Множество всех достижимых клеток
        """
        if not cells:
            return set()
            
        visited = {start}
        queue = deque([start])
        
        while queue:
            x, y = queue.popleft()
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:  # Только прямые соседи
                neighbor = (x + dx, y + dy)
                if neighbor in cells and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
                    
        return visited   