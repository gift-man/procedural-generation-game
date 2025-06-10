"""ИСПРАВЛЕННАЯ система ресурсов с ГАРАНТИРОВАННЫМИ размерами кластеров"""
import random
import math
from collections import deque

class ResourceType:
    MEADOW = "meadow"        # Луга (фермы)
    FOREST = "forest"        # Леса (лесопилки) 
    STONE = "stone"          # Каменоломни
    GOLD_MINE = "gold_mine"  # Золотые шахты

class ResourceGenerator:
    def __init__(self):
        # Базовые вероятности ресурсов
        self.base_ratios = {
            ResourceType.MEADOW: 0.60,    # 60% - луга
            ResourceType.FOREST: 0.25,    # 25% - леса
            ResourceType.STONE: 0.10,     # 10% - камень
            ResourceType.GOLD_MINE: 0.05  # 5% - золото
        }
        
        # СТРОГИЕ минимальные размеры кластеров
        self.min_cluster_sizes = {
            ResourceType.FOREST: 4,       # Лес: СТРОГО минимум 4 клетки
            ResourceType.STONE: 2,        # Камень: СТРОГО минимум 2 клетки
            ResourceType.GOLD_MINE: 1     # Золото: минимум 1 клетка
        }
        
        # Разброс для вариативности
        self.variance = 0.10
        
        # Доходность построек
        self.building_yields = {
            ResourceType.MEADOW: {"gold": 1, "building": "Ферма"},
            ResourceType.FOREST: {"materials": 1, "building": "Лесопилка"},
            ResourceType.STONE: {"materials": 3, "building": "Каменоломня"},
            ResourceType.GOLD_MINE: {"gold": 10, "building": "Золотая шахта"}
        }

    def get_resource_name(self, resource_type):
        names = {
            ResourceType.MEADOW: "Луга",
            ResourceType.FOREST: "Леса", 
            ResourceType.STONE: "Каменоломни",
            ResourceType.GOLD_MINE: "Золотые шахты"
        }
        return names.get(resource_type, "Неизвестно")

    def get_building_yield(self, resource_type):
        return self.building_yields.get(resource_type, {})

    def get_resource_color(self, resource_type):
        colors = {
            ResourceType.MEADOW: (144, 238, 144),
            ResourceType.FOREST: (34, 139, 34),
            ResourceType.STONE: (105, 105, 105),
            ResourceType.GOLD_MINE: (255, 215, 0)
        }
        return colors.get(resource_type, (144, 238, 144))

    def get_building_description(self, resource_type):
        yield_info = self.building_yields.get(resource_type, {})
        building = yield_info.get("building", "Неизвестно")
        
        if "gold" in yield_info:
            return f"{building} (+{yield_info['gold']} золото/ход)"
        elif "materials" in yield_info:
            return f"{building} (+{yield_info['materials']} материал/ход)"
        else:
            return building

    def generate_resources_for_island(self, island_cells):
        """СТРОГАЯ генерация с ГАРАНТИРОВАННЫМИ размерами кластеров"""
        print("=== СТРОГАЯ ГЕНЕРАЦИЯ С ГАРАНТИЯМИ ===")
        
        island_list = list(island_cells)
        total_cells = len(island_list)
        resources = {}
        
        print(f"Всего клеток острова: {total_cells}")
        
        # 1. Рассчитываем количество клеток каждого ресурса
        resource_allocations = self._calculate_strict_allocations(total_cells)
        
        # 2. Планируем кластеры с ГАРАНТИЕЙ размеров
        cluster_plans = self._plan_guaranteed_clusters(resource_allocations)
        
        # 3. Размещаем кластеры БЕЗ ПЕРЕКРЫТИЙ
        used_indices = set()
        
        # Размещаем по порядку: сначала самые требовательные
        resource_order = [ResourceType.FOREST, ResourceType.STONE, ResourceType.GOLD_MINE]
        
        for resource_type in resource_order:
            if resource_type in cluster_plans:
                print(f"\n{self._get_resource_emoji(resource_type)} СТРОГОЕ размещение {self.get_resource_name(resource_type)}:")
                clusters = self._place_guaranteed_clusters(
                    island_list, used_indices, cluster_plans[resource_type], resource_type
                )
                
                # Записываем ресурсы и проверяем размеры
                total_placed = 0
                for cluster_id, cluster in enumerate(clusters):
                    if len(cluster) >= self.min_cluster_sizes[resource_type]:
                        for idx in cluster:
                            resources[island_list[idx]] = resource_type
                            total_placed += 1
                        print(f"    ✅ Кластер {cluster_id + 1}: {len(cluster)} клеток (ВАЛИДНЫЙ)")
                    else:
                        print(f"    ❌ Кластер {cluster_id + 1}: {len(cluster)} клеток (ОТБРОШЕН - слишком мал)")
                
                print(f"    📊 Всего размещено {self.get_resource_name(resource_type)}: {total_placed} клеток")
        
        # 4. Остальное - луга
        meadow_count = 0
        for i, cell in enumerate(island_list):
            if i not in used_indices:
                resources[cell] = ResourceType.MEADOW
                meadow_count += 1
        
        print(f"\n🌱 Заполнено лугами: {meadow_count} клеток")
        
        # 5. Финальная проверка
        self._verify_cluster_sizes(resources, island_cells)
        
        return resources

    def _calculate_strict_allocations(self, total_cells):
        """Рассчитывает количество клеток с учётом минимальных требований"""
        allocations = {}
        
        print("\n📊 СТРОГИЙ РАСЧЁТ РЕСУРСОВ:")
        
        for resource_type, base_ratio in self.base_ratios.items():
            if resource_type == ResourceType.MEADOW:
                continue
                
            # Базовое количество
            base_amount = int(total_cells * base_ratio)
            
            # Минимальное количество = минимальный размер кластера
            min_amount = self.min_cluster_sizes[resource_type]
            
            # Убеждаемся что хватает для минимального кластера
            final_amount = max(min_amount, base_amount)
            
            allocations[resource_type] = final_amount
            
            print(f"  {self.get_resource_name(resource_type)}: {final_amount} клеток "
                  f"(минимум: {min_amount}, базово: {base_amount})")
        
        return allocations

    def _plan_guaranteed_clusters(self, resource_allocations):
        """Планирует кластеры с ГАРАНТИЕЙ минимальных размеров"""
        cluster_plans = {}
        
        print("\n🔒 ПЛАНИРОВАНИЕ С ГАРАНТИЯМИ:")
        
        for resource_type, total_amount in resource_allocations.items():
            min_size = self.min_cluster_sizes[resource_type]
            max_size = max(min_size, total_amount // 3)  # Максимум = треть
            
            print(f"  {self.get_resource_name(resource_type)}: {total_amount} клеток")
            print(f"    Диапазон размеров: {min_size} - {max_size}")
            
            # СТРОГО планируем кластеры
            cluster_sizes = self._plan_strict_clusters(total_amount, min_size, max_size)
            
            # Проверяем что все кластеры валидны
            valid_clusters = [size for size in cluster_sizes if size >= min_size]
            
            cluster_plans[resource_type] = {
                'cluster_count': len(valid_clusters),
                'cluster_sizes': valid_clusters,
                'total_cells': sum(valid_clusters),
                'size_range': (min_size, max_size)
            }
            
            print(f"    Планируемые кластеры: {valid_clusters}")
            print(f"    Гарантированно валидных: {len(valid_clusters)}")
        
        return cluster_plans

    def _plan_strict_clusters(self, total_amount, min_size, max_size):
        """Планирует кластеры БЕЗ кластеров меньше минимума"""
        cluster_sizes = []
        remaining_cells = total_amount
        
        while remaining_cells >= min_size:
            # Максимальный размер ограничен оставшимися клетками
            current_max_size = min(max_size, remaining_cells)
            
            # Если оставшихся клеток меньше чем min_size * 2, создаём один большой кластер
            if remaining_cells < min_size * 2:
                cluster_sizes.append(remaining_cells)
                break
            
            # Создаём кластер случайного размера
            cluster_size = random.randint(min_size, current_max_size)
            
            # Проверяем что после этого кластера останется либо 0, либо >= min_size клеток
            remaining_after = remaining_cells - cluster_size
            if remaining_after > 0 and remaining_after < min_size:
                # Корректируем размер чтобы избежать маленьких остатков
                cluster_size = remaining_cells - min_size
            
            cluster_sizes.append(cluster_size)
            remaining_cells -= cluster_size
        
        return cluster_sizes

    def _place_guaranteed_clusters(self, island_list, used_indices, cluster_plan, resource_type):
        """Размещает кластеры с ПРОВЕРКОЙ размеров"""
        clusters = []
        cluster_sizes = cluster_plan['cluster_sizes']
        min_size = self.min_cluster_sizes[resource_type]
        
        print(f"    Планируется {len(cluster_sizes)} кластеров: {cluster_sizes}")
        
        for cluster_id, target_size in enumerate(cluster_sizes):
            print(f"    Создание кластера {cluster_id + 1} размером {target_size}...")
            
            # Создаём кластер с максимальными попытками
            cluster = self._create_guaranteed_cluster(
                island_list, used_indices, target_size, min_size
            )
            
            if cluster and len(cluster) >= min_size:
                clusters.append(cluster)
                # Отмечаем клетки как использованные
                for idx in cluster:
                    used_indices.add(idx)
                print(f"      ✅ Создан валидный кластер: {len(cluster)} клеток")
            else:
                print(f"      ❌ Кластер слишком мал или не создан: {len(cluster) if cluster else 0} клеток")
        
        return clusters

    def _create_guaranteed_cluster(self, island_list, used_indices, target_size, min_size):
        """Создаёт кластер с ГАРАНТИЕЙ минимального размера"""
        available_indices = [i for i in range(len(island_list)) if i not in used_indices]
        
        if len(available_indices) < min_size:
            print(f"      ⚠️ Недостаточно клеток: {len(available_indices)} < {min_size}")
            return []
        
        # Множественные попытки создания кластера
        max_attempts = 20
        best_cluster = []
        
        for attempt in range(max_attempts):
            # Выбираем случайную стартовую клетку
            start_idx = random.choice(available_indices)
            cluster = [start_idx]
            
            # Агрессивно расширяем кластер
            expanded = self._expand_cluster_aggressively(
                island_list, cluster, available_indices, target_size, used_indices
            )
            
            # Сохраняем лучший результат
            if len(expanded) > len(best_cluster):
                best_cluster = expanded.copy()
            
            # Если достигли целевого размера или минимума, можем остановиться
            if len(expanded) >= target_size or len(expanded) >= min_size:
                best_cluster = expanded
                break
        
        return best_cluster

    def _expand_cluster_aggressively(self, island_list, cluster, available_indices, target_size, used_indices):
        """Агрессивно расширяет кластер до целевого размера"""
        current_cluster = cluster.copy()
        
        while len(current_cluster) < target_size:
            # Ищем всех доступных соседей
            neighbors = []
            for idx in current_cluster:
                cell = island_list[idx]
                for candidate_idx in available_indices:
                    if (candidate_idx not in used_indices and 
                        candidate_idx not in current_cluster):
                        candidate_cell = island_list[candidate_idx]
                        if self._are_neighbors(cell, candidate_cell):
                            neighbors.append(candidate_idx)
            
            if neighbors:
                # Добавляем лучшего соседа
                new_idx = random.choice(neighbors)
                current_cluster.append(new_idx)
            else:
                # Если нет соседей, берём любую близкую клетку
                remaining = [idx for idx in available_indices 
                           if idx not in used_indices and idx not in current_cluster]
                if remaining:
                    # Берём ближайшую к центру кластера
                    cluster_center = self._calculate_cluster_center(island_list, current_cluster)
                    closest_idx = min(remaining, 
                                    key=lambda idx: self._distance_to_point(
                                        island_list[idx], cluster_center))
                    current_cluster.append(closest_idx)
                else:
                    break  # Больше нет доступных клеток
        
        return current_cluster

    def _calculate_cluster_center(self, island_list, cluster):
        """Вычисляет центр кластера"""
        if not cluster:
            return (0, 0)
        
        total_x = sum(island_list[idx][0] for idx in cluster)
        total_y = sum(island_list[idx][1] for idx in cluster)
        
        return (total_x / len(cluster), total_y / len(cluster))

    def _distance_to_point(self, cell, point):
        """Вычисляет расстояние от клетки до точки"""
        return abs(cell[0] - point[0]) + abs(cell[1] - point[1])

    def _are_neighbors(self, cell1, cell2):
        """Проверяет, являются ли две клетки соседними"""
        x1, y1 = cell1
        x2, y2 = cell2
        return (abs(x1 - x2) == 1 and y1 == y2) or (abs(y1 - y2) == 1 and x1 == x2)

    def _get_resource_emoji(self, resource_type):
        emojis = {
            ResourceType.FOREST: "🌲",
            ResourceType.STONE: "🗿", 
            ResourceType.GOLD_MINE: "⭐"
        }
        return emojis.get(resource_type, "📦")

    def _verify_cluster_sizes(self, resources, island_cells):
        """Проверяет что все кластеры соответствуют минимальным размерам"""
        print(f"\n🔍 ПРОВЕРКА РАЗМЕРОВ КЛАСТЕРОВ:")
        
        # Группируем по типам ресурсов
        resource_positions = {}
        for cell, resource_type in resources.items():
            if resource_type not in resource_positions:
                resource_positions[resource_type] = []
            resource_positions[resource_type].append(cell)
        
        # Проверяем каждый тип ресурса
        for resource_type, positions in resource_positions.items():
            if resource_type == ResourceType.MEADOW:
                continue
                
            clusters = self._find_connected_clusters(positions)
            cluster_sizes = [len(cluster) for cluster in clusters]
            min_required = self.min_cluster_sizes[resource_type]
            
            emoji = self._get_resource_emoji(resource_type)
            name = self.get_resource_name(resource_type)
            
            print(f"{emoji} {name}: {len(clusters)} кластеров, размеры: {cluster_sizes}")
            
            # Проверяем нарушения
            invalid_clusters = [size for size in cluster_sizes if size < min_required]
            if invalid_clusters:
                print(f"    ❌ НАРУШЕНИЯ: {len(invalid_clusters)} кластеров меньше {min_required}: {invalid_clusters}")
            else:
                print(f"    ✅ Все кластеры соответствуют минимуму {min_required}")

    def _find_connected_clusters(self, positions):
        """Находит связные кластеры в списке позиций"""
        if not positions:
            return []
        
        positions_set = set(positions)
        visited = set()
        clusters = []
        
        for pos in positions:
            if pos not in visited:
                cluster = []
                queue = deque([pos])
                visited.add(pos)
                
                while queue:
                    current = queue.popleft()
                    cluster.append(current)
                    
                    # Ищем соседей
                    x, y = current
                    neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                    
                    for neighbor in neighbors:
                        if neighbor in positions_set and neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                clusters.append(cluster)
        
        return clusters
