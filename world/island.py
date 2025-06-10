"""Остров с процедурной генерацией и универсальными провинциями"""
from core.settings import *
from world.resources import ResourceGenerator
from world.generator import ProvinceGenerator
import random
import math
from collections import deque

# Встроенные классы для избежания дополнительных файлов
class ProceduralIslandGenerator:
    def __init__(self):
        pass
    
    def generate_connected_island(self, center_x, center_y, target_cells):
        """ГАРАНТИРОВАННО связная генерация острова"""
        print(f"🔗 Связная генерация острова: {target_cells} клеток от центра ({center_x}, {center_y})")
        
        # Начинаем с центральной клетки
        island_cells = {(center_x, center_y)}
        growth_frontier = [(center_x, center_y)]
        
        while len(island_cells) < target_cells and growth_frontier:
            # Выбираем случайную клетку из границы роста
            current_cell = random.choice(growth_frontier)
            x, y = current_cell
            
            # Находим всех доступных соседей
            available_neighbors = []
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor not in island_cells:
                    available_neighbors.append(neighbor)
            
            # Добавляем соседа с высокой вероятностью
            if available_neighbors and random.random() < 0.8:
                new_cell = random.choice(available_neighbors)
                island_cells.add(new_cell)
                growth_frontier.append(new_cell)
                
                # Если достигли цели, прекращаем
                if len(island_cells) >= target_cells:
                    break
            
            # Иногда убираем клетку из границы роста
            if random.random() < 0.3:
                growth_frontier.remove(current_cell)
            
            # Если граница роста пуста, восстанавливаем её
            if not growth_frontier:
                growth_frontier = self._get_border_cells(island_cells)
        
        # Принудительно достигаем целевого размера
        island_cells = self._force_target_size(island_cells, target_cells)
        
        # Проверяем связность
        if not self._is_connected(island_cells):
            print("⚠️ Остров несвязный, исправляем...")
            island_cells = self._ensure_connectivity(island_cells)
        
        print(f"✅ Связный остров: {len(island_cells)} клеток")
        return island_cells
    
    def _get_border_cells(self, island_cells):
        """Находит граничные клетки острова"""
        border = []
        for cell in island_cells:
            x, y = cell
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor not in island_cells:
                    # Эта клетка острова граничит с пустотой
                    if cell not in border:
                        border.append(cell)
                    break
        return border
    
    def _force_target_size(self, island_cells, target_cells):
        """Принудительно достигает целевого размера"""
        island_set = set(island_cells)
        
        while len(island_set) < target_cells:
            # Добавляем соседей к случайным клеткам
            border_cells = self._get_border_cells(island_set)
            if not border_cells:
                break
            
            random_border = random.choice(border_cells)
            x, y = random_border
            
            # Ищем свободного соседа
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor not in island_set:
                    island_set.add(neighbor)
                    break
            
            if len(island_set) >= target_cells:
                break
        
        # Убираем лишние клетки если получилось больше
        while len(island_set) > target_cells:
            border_cells = self._get_border_cells(island_set)
            if border_cells:
                # Убираем случайную граничную клетку
                remove_cell = random.choice(border_cells)
                island_set.remove(remove_cell)
            else:
                break
        
        return island_set
    
    def _is_connected(self, cells):
        """Проверяет связность острова"""
        if not cells:
            return True
        
        cell_set = set(cells)
        start = next(iter(cell_set))
        visited = {start}
        queue = [start]
        
        while queue:
            current = queue.pop(0)
            x, y = current
            
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if neighbor in cell_set and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return len(visited) == len(cell_set)
    
    def _ensure_connectivity(self, cells):
        """Обеспечивает связность острова"""
        cell_set = set(cells)
        
        # Находим все связные компоненты
        components = []
        remaining = cell_set.copy()
        
        while remaining:
            start = next(iter(remaining))
            component = {start}
            queue = [start]
            remaining.remove(start)
            
            while queue:
                current = queue.pop(0)
                x, y = current
                
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    neighbor = (x + dx, y + dy)
                    if neighbor in remaining:
                        component.add(neighbor)
                        queue.append(neighbor)
                        remaining.remove(neighbor)
            
            components.append(component)
        
        # Берем самую большую компоненту
        largest_component = max(components, key=len)
        
        # Соединяем остальные компоненты с самой большой
        for component in components:
            if component != largest_component:
                # Находим ближайшие клетки между компонентами
                min_distance = float('inf')
                bridge_cells = []
                
                for cell1 in largest_component:
                    for cell2 in component:
                        distance = abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])
                        if distance < min_distance:
                            min_distance = distance
                            bridge_cells = [cell1, cell2]
                
                # Строим мостик
                if bridge_cells:
                    path = self._build_path(bridge_cells[0], bridge_cells[1])
                    largest_component.update(path)
                    largest_component.update(component)
        
        return largest_component
    
    def _build_path(self, start, end):
        """Строит простой путь между двумя точками"""
        path = set()
        x1, y1 = start
        x2, y2 = end
        
        # Двигаемся по X
        while x1 != x2:
            path.add((x1, y1))
            x1 += 1 if x2 > x1 else -1
        
        # Двигаемся по Y
        while y1 != y2:
            path.add((x1, y1))
            y1 += 1 if y2 > y1 else -1
        
        path.add((x2, y2))
        return path


class ConnectedProvinceGenerator:
    def __init__(self, island_cells):
        self.island_cells = set(island_cells)
        self.cell_list = list(island_cells)
        
    def generate_provinces(self):
        """Генерирует связные провинции оптимального размера"""
        island_size = len(self.island_cells)
        
        # Определяем оптимальное количество провинций
        if island_size <= 15:
            target_provinces = 1
        elif island_size <= 25:
            target_provinces = 2
        elif island_size <= 40:
            target_provinces = 3
        elif island_size <= 60:
            target_provinces = 4
        else:
            target_provinces = min(6, island_size // 15)
        
        print(f"🗺️ Генерация {target_provinces} связных провинций для острова из {island_size} клеток")
        
        if target_provinces == 1:
            # Весь остров - одна провинция
            return [{'cells': self.cell_list}], {cell: 0 for cell in self.cell_list}
        
        # Генерируем связные провинции методом "растущих областей"
        return self._generate_connected_regions(target_provinces)
    
    def _generate_connected_regions(self, target_provinces):
        """Генерирует связные провинции методом растущих областей"""
        
        # Выбираем стартовые точки максимально удаленные друг от друга
        seed_points = self._select_distributed_seeds(target_provinces)
        
        # Инициализируем провинции
        provinces = []
        province_map = {}
        growth_queues = []
        
        for i, seed in enumerate(seed_points):
            provinces.append({'cells': [seed]})
            province_map[seed] = i
            growth_queues.append(deque([seed]))
        
        # Растим провинции поочередно
        remaining_cells = set(self.island_cells) - set(seed_points)
        
        while remaining_cells:
            grown_this_round = False
            
            # Сортируем провинции по размеру (меньшие растут первыми)
            province_order = sorted(range(len(provinces)), 
                                  key=lambda i: len(provinces[i]['cells']))
            
            for province_id in province_order:
                if not growth_queues[province_id] or not remaining_cells:
                    continue
                
                # Берем клетку из очереди роста этой провинции
                current_cell = growth_queues[province_id].popleft()
                x, y = current_cell
                
                # Ищем доступных соседей
                available_neighbors = []
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    neighbor = (x + dx, y + dy)
                    if neighbor in remaining_cells:
                        available_neighbors.append(neighbor)
                
                # Добавляем одного соседа (если есть)
                if available_neighbors:
                    new_cell = random.choice(available_neighbors)
                    provinces[province_id]['cells'].append(new_cell)
                    province_map[new_cell] = province_id
                    remaining_cells.remove(new_cell)
                    growth_queues[province_id].append(new_cell)
                    grown_this_round = True
                
                if not remaining_cells:
                    break
            
            # Если никто не смог вырасти, назначаем оставшиеся клетки
            if not grown_this_round and remaining_cells:
                for cell in list(remaining_cells):
                    closest_province = self._find_closest_province(cell, province_map)
                    provinces[closest_province]['cells'].append(cell)
                    province_map[cell] = closest_province
                    remaining_cells.remove(cell)
        
        # Проверяем результат
        print(f"✅ Связные провинции созданы:")
        for i, province in enumerate(provinces):
            print(f"   Провинция {i}: {len(province['cells'])} клеток")
        
        return provinces, province_map
    
    def _select_distributed_seeds(self, count):
        """Выбирает максимально распределенные стартовые точки"""
        if count >= len(self.cell_list):
            return self.cell_list[:count]
        
        seeds = [random.choice(self.cell_list)]
        
        while len(seeds) < count:
            best_candidate = None
            best_min_distance = 0
            
            # Ищем точку максимально удаленную от всех уже выбранных
            for candidate in self.cell_list:
                if candidate in seeds:
                    continue
                
                min_distance = min(
                    abs(candidate[0] - seed[0]) + abs(candidate[1] - seed[1])
                    for seed in seeds
                )
                
                if min_distance > best_min_distance:
                    best_min_distance = min_distance
                    best_candidate = candidate
            
            if best_candidate:
                seeds.append(best_candidate)
            else:
                # Если не нашли, берем случайную свободную
                available = [c for c in self.cell_list if c not in seeds]
                if available:
                    seeds.append(random.choice(available))
        
        return seeds
    
    def _find_closest_province(self, cell, province_map):
        """Находит ближайшую провинцию для клетки"""
        min_distance = float('inf')
        closest_province = 0
        
        for mapped_cell, province_id in province_map.items():
            distance = abs(cell[0] - mapped_cell[0]) + abs(cell[1] - mapped_cell[1])
            if distance < min_distance:
                min_distance = distance
                closest_province = province_id
        
        return closest_province

# Основной класс острова
class Island:
    def __init__(self):
        self.cells = set()
        self.resources = {}
        self.resource_generator = ResourceGenerator()
        self.procedural_generator = ProceduralIslandGenerator()
        
        # Информация об островах
        self.islands_info = []
        
        self.load_from_matrix()
        self.generate_resources()
        
    def _generate_connected_island(self, center_x, center_y, target_size):
        """Обертка для связной генерации острова"""
        return self.procedural_generator.generate_connected_island(center_x, center_y, target_size)
    
    def load_from_matrix(self):
        """Загружает статический основной остров + генерирует процедурные острова"""
        print("=== ГЕНЕРАЦИЯ ОСТРОВОВ ===")
        
        # 1. Основной остров (статический - всегда одинаковый)
        main_island_cells = set()
        for row_idx, row in enumerate(ISLAND_MATRIX):
            for col_idx, cell in enumerate(row):
                if cell == 1:
                    x = col_idx + ISLAND_OFFSET_X
                    y = row_idx + ISLAND_OFFSET_Y
                    self.cells.add((x, y))
                    main_island_cells.add((x, y))
        
        self.islands_info.append({
            'name': 'Главный остров',
            'cells': main_island_cells,
            'type': 'main',
            'provinces': [],
            'province_map': {}
        })
        
        print(f"Главный остров загружен: {len(main_island_cells)} клеток")
        
        # 2. ПРОЦЕДУРНЫЕ дополнительные острова
        self._generate_additional_islands()
        
        print(f"Всего клеток суши: {len(self.cells)}")
    
    def _generate_additional_islands(self):
        """ИСПРАВЛЕННАЯ генерация с проверкой границ"""
        
        # ФИКСИРОВАННОЕ количество островов
        num_islands = 2  # Всегда 2 дополнительных острова
        main_max_x = max(cell[0] for cell in self.cells) if self.cells else 15
        
        for island_num in range(num_islands):
            # ИСПРАВЛЕНО: Строгое позиционирование в границах экрана
            if island_num == 0:
                # Первый остров - близко к основному
                center_x = main_max_x + 4
                center_y = ISLAND_OFFSET_Y + 3
            else:
                # Второй остров - правее первого
                center_x = main_max_x + 8
                center_y = ISLAND_OFFSET_Y + 6
            
            # ЖЕСТКИЕ ограничения по границам экрана
            max_allowed_x = (SCREEN_WIDTH // CELL_SIZE) - 8  # Отступ в 8 клеток от края
            max_allowed_y = (SCREEN_HEIGHT // CELL_SIZE) - 8
            
            center_x = min(center_x, max_allowed_x)
            center_y = min(center_y, max_allowed_y)
            center_y = max(center_y, 5)  # Минимум 5 клеток от верха
            
            print(f"🏝️ Остров #{island_num + 1}: позиция ({center_x}, {center_y})")
            print(f"   Границы экрана: макс X={max_allowed_x}, макс Y={max_allowed_y}")
            
            # Генерируем МАЛЕНЬКИЙ остров
            new_island_cells = self.procedural_generator.generate_island(
                center_x, center_y, "small"  # ТОЛЬКО маленькие острова
            )
            
            # СТРОГАЯ проверка границ экрана
            valid_cells = set()
            for cell in new_island_cells:
                x, y = cell
                if (0 <= x < (SCREEN_WIDTH // CELL_SIZE) - 2 and 
                    0 <= y < (SCREEN_HEIGHT // CELL_SIZE) - 2):
                    valid_cells.add(cell)
            
            # ПРОВЕРКА на пересечение с существующими островами
            if self._check_island_separation(valid_cells):
                self.cells.update(valid_cells)
                
                self.islands_info.append({
                    'name': f'Остров #{island_num + 1}',
                    'cells': valid_cells,
                    'type': 'procedural',
                    'provinces': [],
                    'province_map': {}
                })
                
                print(f"✅ Остров #{island_num + 1} создан: {len(valid_cells)} клеток")
            else:
                print(f"❌ Остров #{island_num + 1} отклонен - пересекается с другими")

    def _check_island_separation(self, new_island_cells):
        """Проверяет что новый остров не пересекается с существующими"""
        min_distance = 2  # Минимум 2 клетки между островами
        
        for new_cell in new_island_cells:
            for existing_cell in self.cells:
                distance = max(abs(new_cell[0] - existing_cell[0]), 
                            abs(new_cell[1] - existing_cell[1]))
                if distance < min_distance:
                    return False
        return True

    
    def generate_provinces_for_islands(self):
        """УНИВЕРСАЛЬНАЯ генерация - ОДИНАКОВАЯ логика для ВСЕХ островов"""
        print("\n=== УНИВЕРСАЛЬНАЯ ГЕНЕРАЦИЯ ПРОВИНЦИЙ ===")
        
        all_provinces = []
        all_province_map = {}
        province_id_offset = 0
        
        for island_info in self.islands_info:
            island_name = island_info['name']
            island_cells = island_info['cells']
            island_type = island_info['type']
            
            print(f"\n🏝️ Обработка {island_name} ({len(island_cells)} клеток):")
            
            if len(island_cells) < 10:
                print(f"   ⚠️ Остров слишком мал для провинций")
                continue
            
            # ЕДИНАЯ ЛОГИКА: адаптивный генератор для ВСЕХ островов
            print("   🎯 Используем АДАПТИВНЫЙ генератор для всех островов")
            temp_island = self._create_temp_island(island_cells)
            province_gen = ProvinceGenerator(temp_island)
            
            # КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ: масштабируем целевое количество провинций
            if island_type == 'main':
                # Для основного острова - 15 провинций
                province_gen.target_province_count = 15
            else:
                # Для дополнительных островов - ПРОПОРЦИОНАЛЬНОЕ количество
                main_island_size = len(self.islands_info[0]['cells'])  # Размер основного
                current_island_size = len(island_cells)
                
                # Пропорциональное масштабирование: 15 провинций * (размер_острова / размер_основного)
                proportional_count = int(15 * (current_island_size / main_island_size))
                proportional_count = max(3, min(proportional_count, 8))  # От 3 до 8 провинций
                
                province_gen.target_province_count = proportional_count
                print(f"   📊 Пропорциональное количество провинций: {proportional_count}")
            
            # ОДИНАКОВЫЕ настройки для всех островов
            province_gen.MAX_ATTEMPTS = 10000
            
            island_provinces, island_province_map = province_gen.generate_provinces()
            
            # Преобразуем результат
            formatted_provinces = []
            for i, province in enumerate(island_provinces):
                formatted_provinces.append({
                    'id': i + province_id_offset,
                    'cells': province['cells'],
                    'island': island_name
                })
            
            # Корректируем ID в карте провинций
            corrected_map = {
                cell: pid + province_id_offset 
                for cell, pid in island_province_map.items()
            }
            
            # Добавляем к общему результату
            all_provinces.extend(formatted_provinces)
            all_province_map.update(corrected_map)
            
            # Сохраняем в информации об острове
            island_info['provinces'] = formatted_provinces
            island_info['province_map'] = corrected_map
            
            province_id_offset += len(formatted_provinces)
            
            print(f"   ✅ Создано {len(formatted_provinces)} провинций")
        
        print(f"\n🎯 ИТОГО: {len(all_provinces)} провинций на {len(self.islands_info)} островах")
        print(f"\n🔍 ОТЛАДКА ПОЗИЦИОНИРОВАНИЯ:")
        print(f"   Размер экрана: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        print(f"   Максимальные координаты: X={SCREEN_WIDTH//CELL_SIZE}, Y={SCREEN_HEIGHT//CELL_SIZE}")

        for island_info in self.islands_info:
            if island_info['cells']:
                min_x = min(cell[0] for cell in island_info['cells'])
                max_x = max(cell[0] for cell in island_info['cells'])
                min_y = min(cell[1] for cell in island_info['cells'])
                max_y = max(cell[1] for cell in island_info['cells'])
                
                print(f"   {island_info['name']}: X({min_x}-{max_x}), Y({min_y}-{max_y})")
                
                if max_x >= SCREEN_WIDTH//CELL_SIZE:
                    print(f"     ❌ ВЫХОДИТ ЗА ПРАВУЮ ГРАНИЦУ!")
                if max_y >= SCREEN_HEIGHT//CELL_SIZE:
                    print(f"     ❌ ВЫХОДИТ ЗА НИЖНЮЮ ГРАНИЦУ!")
        return all_provinces, all_province_map
    
    def _calculate_island_distribution(self, total_cells=100):
        """Случайное распределение общего количества клеток между островами"""
        
        distributions = [
            # [количество_островов, минимальный_размер_каждого]
            ([1], [total_cells]),  # 1 большой остров
            ([2], [total_cells // 2, total_cells - total_cells // 2]),  # 2 острова
            ([3], [total_cells // 3, total_cells // 3, total_cells - 2 * (total_cells // 3)]),  # 3 острова
            ([4], [total_cells // 4] * 4),  # 4 острова по 25
        ]
        
        # Фильтруем варианты где все острова >= 4 клеток
        valid_distributions = []
        for counts, sizes in distributions:
            if all(size >= 4 for size in sizes):
                valid_distributions.append((counts, sizes))
        
        # Выбираем случайный вариант
        chosen_counts, base_sizes = random.choice(valid_distributions)
        
        print(f"🎲 Выбрано распределение: {len(base_sizes)} островов размерами {base_sizes}")
        return base_sizes

    def _generate_additional_islands(self):
        """НОВАЯ система с контролируемым распределением размеров"""
        
        # Определяем распределение размеров
        island_sizes = self._calculate_island_distribution(100)
        
        main_max_x = max(cell[0] for cell in self.cells) if self.cells else 15
        
        for island_num, target_size in enumerate(island_sizes):
            # Позиционирование островов
            if island_num == 0:
                center_x = main_max_x + 5
                center_y = ISLAND_OFFSET_Y + 3
            elif island_num == 1:
                center_x = main_max_x + 12
                center_y = ISLAND_OFFSET_Y + 6
            elif island_num == 2:
                center_x = main_max_x + 8
                center_y = ISLAND_OFFSET_Y + 10
            else:
                center_x = main_max_x + 15
                center_y = ISLAND_OFFSET_Y + 2
            
            # Жесткие ограничения границ
            max_allowed_x = (SCREEN_WIDTH // CELL_SIZE) - 10
            max_allowed_y = (SCREEN_HEIGHT // CELL_SIZE) - 10
            
            center_x = min(center_x, max_allowed_x)
            center_y = min(center_y, max_allowed_y)
            center_y = max(center_y, 5)
            
            print(f"🏝️ Генерация острова #{island_num + 1}: цель {target_size} клеток в позиции ({center_x}, {center_y})")
            
            # НОВЫЙ алгоритм связной генерации
            new_island_cells = self._generate_connected_island(center_x, center_y, target_size)
            
            # Проверяем разделение островов
            if self._check_island_separation(new_island_cells):
                self.cells.update(new_island_cells)
                
                self.islands_info.append({
                    'name': f'Остров #{island_num + 1}',
                    'cells': new_island_cells,
                    'type': 'procedural',
                    'provinces': [],
                    'province_map': {}
                })
                
                print(f"✅ Остров #{island_num + 1} создан: {len(new_island_cells)} клеток")
            else:
                print(f"❌ Остров #{island_num + 1} пересекается - пропускаем")
        
    def _create_temp_island(self, island_cells):
        """Создает временный объект острова для генератора провинций"""
        class TempIsland:
            def __init__(self, cells):
                self.cells = set(cells)
        
        return TempIsland(island_cells)
    
    def generate_resources(self):
        """Генерирует ресурсы для всех островов"""
        print("Генерация ресурсов для всех островов...")
        self.resources.clear()
        
        for island_info in self.islands_info:
            island_name = island_info['name']
            island_cells = island_info['cells']
            island_type = island_info['type']
            
            print(f"\nГенерация ресурсов для {island_name}:")
            
            if island_type == 'main':
                island_resources = self.resource_generator.generate_resources_for_island(island_cells)
            else:
                # Для процедурных островов - особая генерация
                if hasattr(self.resource_generator, 'generate_resources_for_secondary_island'):
                    island_resources = self.resource_generator.generate_resources_for_secondary_island(island_cells)
                else:
                    island_resources = self.resource_generator.generate_resources_for_island(island_cells)
            
            self.resources.update(island_resources)
        
        self._print_total_stats()
    
    def _print_total_stats(self):
        """Выводит статистику по островам"""
        print(f"\n=== СТАТИСТИКА ОСТРОВОВ ===")
        for island_info in self.islands_info:
            island_name = island_info['name']
            island_cells = island_info['cells']
            
            print(f"\n{island_name} ({len(island_cells)} клеток):")
            resource_counts = {}
            for cell in island_cells:
                resource = self.resources.get(cell)
                if resource:
                    resource_counts[resource] = resource_counts.get(resource, 0) + 1
            
            for resource_type, count in resource_counts.items():
                name = self.resource_generator.get_resource_name(resource_type)
                percentage = (count / len(island_cells)) * 100
                print(f"   {name}: {count} клеток ({percentage:.1f}%)")
    
    def regenerate_islands(self):
        """Перегенерирует все острова"""
        print("\n=== ПЕРЕГЕНЕРАЦИЯ ОСТРОВОВ ===")
        
        # Очищаем данные
        self.cells.clear()
        self.resources.clear()
        self.islands_info.clear()
        
        # Перегенерируем
        self.load_from_matrix()
        self.generate_resources()
        
        print("✅ Острова перегенерированы")
    
    # Методы совместимости и утилиты
    def get_island_info(self):
        """Возвращает информацию о всех островах"""
        return self.islands_info
    
    def get_island_by_cell(self, x, y):
        """Определяет к какому острову принадлежит клетка"""
        for island_info in self.islands_info:
            if (x, y) in island_info['cells']:
                return island_info
        return None
    
    def get_resource(self, x, y):
        """Возвращает ресурс клетки"""
        return self.resources.get((x, y))
    
    def is_land(self, x, y):
        """Проверяет, является ли клетка сушей"""
        return (x, y) in self.cells
    
    def get_neighbors(self, x, y):
        """Возвращает соседние клетки суши"""
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if self.is_land(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
    
    def get_total_cells(self):
        """Возвращает общее количество клеток суши"""
        return len(self.cells)
    
    def get_islands_count(self):
        """Возвращает количество островов"""
        return len(self.islands_info)
    
    def get_island_names(self):
        """Возвращает названия всех островов"""
        return [island['name'] for island in self.islands_info]
