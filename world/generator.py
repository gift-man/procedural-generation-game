"""Генератор провинций - АДАПТИВНОЕ КОЛИЧЕСТВО ПРОВИНЦИЙ"""
import random
import math
from collections import deque
from core.settings import *

class ProvinceGenerator:
    def __init__(self, island):
        self.island = island
        # Ограничения для предотвращения бесконечных циклов
        self.MAX_ATTEMPTS = 1000
        self.target_province_count = None  # Может быть установлено извне для фиксированного количества
        
        # Анализ острова будет сохранен здесь
        self.island_analysis = None
    
    def generate_provinces(self):
        """ОСНОВНОЙ метод генерации провинций"""
        print("🎯 СТАРТ ГЕНЕРАЦИИ ПРОВИНЦИЙ")
        
        try:
            # Пробуем умную адаптивную генерацию
            result = self._smart_adaptive_generation()
            
            if result:
                provinces, province_map = result
                print(f"✅ Умная генерация успешна: {len(provinces)} провинций")
                return provinces, province_map
            else:
                print("⚠️ Умная генерация вернула None")
                
        except Exception as e:
            print(f"⚠️ Ошибка умной генерации: {e}")
        
        # Если умная генерация не сработала, используем простую
        try:
            print("🚨 Переход к экстренной генерации...")
            provinces, province_map = self._emergency_fallback()
            print(f"✅ Экстренная генерация: {len(provinces)} провинций")
            return provinces, province_map
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return [], {}
    
    def _smart_adaptive_generation(self):
        """УМНАЯ генерация с адаптивным количеством провинций"""
        print("🎯 УМНАЯ ГЕНЕРАЦИЯ С АДАПТИВНЫМ КОЛИЧЕСТВОМ ПРОВИНЦИЙ")
        
        # Анализируем остров и определяем оптимальное количество провинций
        analysis = self._analyze_island()
        
        # Используем заданное целевое количество, если оно указано
        if self.target_province_count is not None:
            target_provinces = self.target_province_count
            print(f"   Заданное количество провинций: {target_provinces}")
        else:
            target_provinces = analysis['optimal_provinces']
            print(f"   Оптимальное количество провинций: {target_provinces}")
        
        attempt = 0
        best_result = None
        
        # Ограничиваем количество попыток
        while attempt < self.MAX_ATTEMPTS:
            attempt += 1
            
            if attempt % 50 == 0:
                print(f"Попытка {attempt}... Ищем генерацию с {target_provinces} провинциями...")
            
            try:
                result = self._smart_attempt(target_provinces)
                if result:
                    provinces_list, province_map = result
                    
                    # Сохраняем как лучший результат
                    if self._is_good_enough_result(provinces_list, province_map):
                        best_result = result
                    
                    # Если идеально - возвращаем сразу
                    if self._is_absolutely_perfect(provinces_list, province_map):
                        print(f"\n🎉 ИДЕАЛЬНАЯ ГЕНЕРАЦИЯ за {attempt} попыток!")
                        self._print_adaptive_result(provinces_list, province_map, target_provinces)
                        return provinces_list, province_map
                    
            except Exception:
                continue
        
        # Если не нашли идеального, но есть приемлемый результат
        if best_result:
            print(f"✅ Используем лучший найденный результат за {self.MAX_ATTEMPTS} попыток")
            return best_result
        
        # Если ничего не получилось
        print(f"⚠️ Не удалось найти хороший результат за {self.MAX_ATTEMPTS} попыток")
        return self._emergency_fallback()
    
    def _analyze_island(self):
        """Анализирует структуру острова"""
        island_cells = list(self.island.cells)
        total_cells = len(island_cells)
        
        min_x = min(cell[0] for cell in island_cells)
        max_x = max(cell[0] for cell in island_cells)
        min_y = min(cell[1] for cell in island_cells)
        max_y = max(cell[1] for cell in island_cells)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        density = total_cells / (width * height)
        
        # Вычисляем оптимальное количество провинций
        optimal_provinces = self._calculate_optimal_province_count(total_cells)
        
        # Находим центральные клетки (хорошие для семян)
        central_cells = []
        for cell in island_cells:
            neighbor_count = 0
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    neighbor = (cell[0] + dx, cell[1] + dy)
                    if neighbor in self.island.cells:
                        neighbor_count += 1
            
            if neighbor_count >= 6:
                central_cells.append(cell)
        
        self.island_analysis = {
            'bounds': (min_x, max_x, min_y, max_y),
            'dimensions': (width, height),
            'total_cells': total_cells,
            'density': density,
            'central_cells': central_cells,
            'optimal_provinces': optimal_provinces,
            'optimal_seed_distance': max(3, int(math.sqrt(total_cells / optimal_provinces)))
        }
        
        return self.island_analysis
    
    def _calculate_optimal_province_count(self, total_cells):
        """Вычисляет оптимальное количество провинций"""
        
        # Если задано целевое количество, используем его
        if self.target_province_count is not None:
            return self.target_province_count
        
        options = []
        
        # Проверяем разные варианты количества провинций
        for province_count in range(10, 20):
            avg_size = total_cells / province_count
            
            # Проверяем, подходит ли этот вариант
            if MIN_PROVINCE_SIZE <= avg_size <= MAX_PROVINCE_SIZE:
                # Вычисляем "качество" этого варианта
                ideal_size = 6
                size_score = 1.0 - abs(avg_size - ideal_size) / ideal_size
                
                # Предпочитаем количество провинций ближе к 15
                count_score = 1.0 - abs(province_count - 15) / 15
                
                # Общая оценка
                total_score = size_score * 0.7 + count_score * 0.3
                
                options.append({
                    'count': province_count,
                    'avg_size': avg_size,
                    'score': total_score
                })
        
        if not options:
            return 15  # Резервный вариант
        
        # Выбираем лучший вариант
        best_option = max(options, key=lambda x: x['score'])
        return best_option['count']
    
    def _smart_attempt(self, target_provinces):
        """Попытка умной генерации с заданным количеством провинций"""
        seeds = self._get_adaptive_seeds(target_provinces)
        
        if len(seeds) < target_provinces * 0.8:
            return None
        
        province_map = {}
        provinces_list = []
        
        for i, seed in enumerate(seeds):
            province_map[seed] = i
            provinces_list.append({"cells": [seed]})
        
        unassigned = set(self.island.cells) - set(seeds)
        
        # Умный рост с адаптивным целевым размером
        for round_num in range(100):
            if not unassigned:
                break
                
            grown_this_round = False
            
            # Сортируем провинции по размеру (меньшие растут первыми)
            province_order = sorted(range(len(seeds)), 
                                  key=lambda i: len(provinces_list[i]["cells"]))
            
            for province_id in province_order:
                current_size = len(provinces_list[province_id]["cells"])
                
                if current_size >= MAX_PROVINCE_SIZE:
                    continue
                
                best_cell = self._find_best_next_cell(
                    provinces_list[province_id]["cells"], 
                    unassigned, 
                    province_map, 
                    province_id
                )
                
                if best_cell:
                    province_map[best_cell] = province_id
                    provinces_list[province_id]["cells"].append(best_cell)
                    unassigned.remove(best_cell)
                    grown_this_round = True
                
                if not unassigned:
                    break
            
            if not grown_this_round:
                break
        
        # Умное распределение оставшихся клеток
        provinces_list, province_map = self._smart_distribute_remaining(
            provinces_list, province_map, unassigned
        )
        
        return provinces_list, province_map
    
    def _get_adaptive_seeds(self, target_provinces):
        """Получает семена для адаптивного количества провинций"""
        analysis = self.island_analysis
        candidates = analysis['central_cells'].copy()
        
        if not candidates:
            candidates = list(self.island.cells)
        
        random.shuffle(candidates)
        seeds = []
        min_distance = analysis['optimal_seed_distance']
        
        # Адаптивное расстояние в зависимости от количества провинций
        if target_provinces > 15:
            min_distance = max(2, min_distance - 1)
        elif target_provinces < 12:
            min_distance += 1
        
        for cell in candidates:
            if len(seeds) >= target_provinces:
                break
                
            good_position = True
            for seed in seeds:
                distance = abs(cell[0] - seed[0]) + abs(cell[1] - seed[1])
                if distance < min_distance:
                    good_position = False
                    break
            
            if good_position:
                seeds.append(cell)
        
        # Добавляем семена с менее строгими требованиями если нужно
        if len(seeds) < target_provinces:
            edge_cells = [cell for cell in self.island.cells if cell not in analysis['central_cells']]
            random.shuffle(edge_cells)
            
            for cell in edge_cells:
                if len(seeds) >= target_provinces:
                    break
                    
                good_position = True
                for seed in seeds:
                    distance = abs(cell[0] - seed[0]) + abs(cell[1] - seed[1])
                    if distance < min_distance - 1:
                        good_position = False
                        break
                
                if good_position:
                    seeds.append(cell)
        
        return seeds
    
    def _find_best_next_cell(self, province_cells, unassigned, province_map, province_id):
        """Находит лучшую следующую клетку для провинции"""
        candidates = []
        for cell in province_cells:
            for neighbor in self._get_neighbors(cell[0], cell[1]):
                if neighbor in unassigned:
                    candidates.append(neighbor)
        
        if not candidates:
            return None
        
        best_cell = None
        best_score = -1
        
        for candidate in candidates:
            score = self._evaluate_cell(candidate, province_cells, province_map, province_id)
            if score > best_score:
                best_score = score
                best_cell = candidate
        
        return best_cell if best_score > 0 else None
    
    def _evaluate_cell(self, cell, province_cells, province_map, province_id):
        """Оценивает качество добавления клетки к провинции"""
        test_cells = province_cells + [cell]
        score = 0
        
        # Проверяем связность
        if not self._is_connected(test_cells):
            return -1000
        
        # Проверяем размер
        if len(test_cells) > MAX_PROVINCE_SIZE:
            return -1000
        
        # Проверяем плюсовые пересечения
        if self._would_create_plus(cell[0], cell[1], province_map, province_id):
            return -1000
        
        # Вычисляем компактность
        compactness = self._calculate_compactness(test_cells)
        score += compactness * 100
        
        # Бонус за центральные клетки
        if hasattr(self, 'island_analysis') and cell in self.island_analysis['central_cells']:
            score += 50
        
        # Бонус за клетки с большим количеством соседей
        neighbor_count = sum(1 for neighbor in self._get_neighbors(cell[0], cell[1]) 
                           if neighbor in self.island.cells)
        score += neighbor_count * 10
        
        return score
    
    def _smart_distribute_remaining(self, provinces_list, province_map, unassigned):
        """Умно распределяет оставшиеся клетки"""
        for cell in list(unassigned):
            best_province = None
            best_score = -1
            
            for prov_id, province in enumerate(provinces_list):
                if len(province["cells"]) >= MAX_PROVINCE_SIZE:
                    continue
                
                test_cells = province["cells"] + [cell]
                if (self._is_connected(test_cells) and
                    not self._would_create_plus(cell[0], cell[1], province_map, prov_id)):
                    
                    score = self._calculate_compactness(test_cells)
                    if score > best_score:
                        best_score = score
                        best_province = prov_id
            
            if best_province is not None:
                province_map[cell] = best_province
                provinces_list[best_province]["cells"].append(cell)
                unassigned.remove(cell)
        
        return provinces_list, province_map
    
    def _is_good_enough_result(self, provinces_list, province_map):
        """Проверяет, достаточно ли хорош результат"""
        if not provinces_list:
            return False
        
        # Все клетки должны быть назначены
        total_assigned = sum(len(prov["cells"]) for prov in provinces_list)
        if total_assigned != len(self.island.cells):
            return False
        
        # Провинции должны быть в разумных размерах
        for province in provinces_list:
            size = len(province["cells"])
            if size < MIN_PROVINCE_SIZE or size > MAX_PROVINCE_SIZE:
                return False
        
        return True
    
    def _is_absolutely_perfect(self, provinces_list, province_map):
        """Проверяет идеальность результата"""
        if not self._is_good_enough_result(provinces_list, province_map):
            return False
        
        # Проверяем связность всех провинций
        for province in provinces_list:
            if not self._is_connected(province["cells"]):
                return False
        
        # Проверяем отсутствие плюсовых пересечений
        if self._count_plus_intersections(province_map) != 0:
            return False
        
        return True
    
    def _emergency_fallback(self):
        """Экстренная простая генерация"""
        print("🚨 ЭКСТРЕННАЯ ГЕНЕРАЦИЯ")
        
        island_cells = list(self.island.cells)
        target_provinces = min(8, len(island_cells) // 6)
        province_size = len(island_cells) // target_provinces
        
        provinces = []
        province_map = {}
        
        for i in range(target_provinces):
            start_idx = i * province_size
            if i == target_provinces - 1:
                end_idx = len(island_cells)
            else:
                end_idx = start_idx + province_size
            
            province_cells = island_cells[start_idx:end_idx]
            
            provinces.append({
                "cells": province_cells
            })
            
            for cell in province_cells:
                province_map[cell] = i
        
        print(f"✅ Экстренная генерация: {len(provinces)} провинций")
        return provinces, province_map
    
    # Вспомогательные функции
    def _get_neighbors(self, x, y):
        """Возвращает соседние координаты"""
        return [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
    
    def _is_connected(self, cells):
        """Проверяет связность набора клеток"""
        if not cells or len(cells) <= 1:
            return True
        
        cells_set = set(cells)
        start_cell = next(iter(cells_set))
        visited = {start_cell}
        queue = deque([start_cell])
        
        while queue:
            current = queue.popleft()
            for neighbor in self._get_neighbors(current[0], current[1]):
                if neighbor in cells_set and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        
        return len(visited) == len(cells_set)
    
    def _would_create_plus(self, x, y, province_map, new_province_id):
        """Проверяет, создаст ли клетка плюсовое пересечение"""
        corner_points = [(x, y), (x+1, y), (x, y+1), (x+1, y+1)]
        
        for corner_x, corner_y in corner_points:
            cells_around_corner = [
                (corner_x-1, corner_y-1), (corner_x, corner_y-1),
                (corner_x-1, corner_y), (corner_x, corner_y)
            ]
            
            provinces_at_corner = set()
            for cell in cells_around_corner:
                if cell == (x, y):
                    provinces_at_corner.add(new_province_id)
                elif cell in province_map:
                    provinces_at_corner.add(province_map[cell])
            
            if len(provinces_at_corner) >= 4:
                return True
        
        return False
    
    def _calculate_compactness(self, cells):
        """Вычисляет компактность провинции"""
        if len(cells) <= 2:
            return 1.0
        
        center_x = sum(x for x, y in cells) / len(cells)
        center_y = sum(y for x, y in cells) / len(cells)
        
        avg_distance = sum(math.sqrt((x - center_x)**2 + (y - center_y)**2) for x, y in cells) / len(cells)
        ideal_radius = math.sqrt(len(cells) / math.pi)
        
        return ideal_radius / avg_distance if avg_distance > 0 else 1.0
    
    def _count_plus_intersections(self, province_map):
        """Подсчитывает количество плюсовых пересечений"""
        plus_count = 0
        
        min_x = min(cell[0] for cell in self.island.cells)
        max_x = max(cell[0] for cell in self.island.cells)
        min_y = min(cell[1] for cell in self.island.cells)
        max_y = max(cell[1] for cell in self.island.cells)
        
        for gx in range(min_x, max_x + 1):
            for gy in range(min_y, max_y + 1):
                corners = [(gx, gy), (gx+1, gy), (gx, gy+1), (gx+1, gy+1)]
                provinces_here = set()
                
                for corner in corners:
                    if corner in province_map:
                        provinces_here.add(province_map[corner])
                
                if len(provinces_here) >= 4:
                    plus_count += 1
        
        return plus_count
    
    def _print_adaptive_result(self, provinces_list, province_map, target_provinces):
        """Выводит результат адаптивной генерации"""
        print("\n🏆 ИДЕАЛЬНАЯ АДАПТИВНАЯ ГЕНЕРАЦИЯ!")
        print("=" * 60)
        
        total_cells = sum(len(prov["cells"]) for prov in provinces_list)
        sizes_distribution = {}
        total_compactness = 0
        
        for i, province in enumerate(provinces_list):
            size = len(province["cells"])
            compactness = self._calculate_compactness(province["cells"])
            total_compactness += compactness
            
            sizes_distribution[size] = sizes_distribution.get(size, 0) + 1
            print(f"Провинция {i+1}: {size} клеток, компактность: {compactness:.2f}")
        
        avg_compactness = total_compactness / len(provinces_list)
        avg_size = total_cells / len(provinces_list)
        
        print(f"\n📊 АДАПТИВНАЯ СТАТИСТИКА:")
        print(f"   Целевое количество провинций: {target_provinces}")
        print(f"   Фактическое количество: {len(provinces_list)}")
        print(f"   Средний размер провинции: {avg_size:.1f} клеток")
        print(f"   Всего клеток: {total_cells}/{len(self.island.cells)}")
        print(f"   Средняя компактность: {avg_compactness:.2f}")
        print(f"   Распределение размеров: {sizes_distribution}")
        print("\n✨ АДАПТИВНАЯ ГЕНЕРАЦИЯ ДОСТИГЛА СОВЕРШЕНСТВА! ✨")
