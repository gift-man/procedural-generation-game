"""Универсальный генератор связных провинций"""
import random
from collections import deque

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
