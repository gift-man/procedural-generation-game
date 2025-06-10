# world/procedural_island_generator.py
import random
import math

class ProceduralIslandGenerator:
    def generate_island(self, center_x, center_y, target_cells):
        """ГАРАНТИРОВАННО связная генерация острова"""
        island_cells = {(center_x, center_y)}
        frontier = [(center_x, center_y)]

        while len(island_cells) < target_cells and frontier:
            current_cell = random.choice(frontier)
            x, y = current_cell

            # Добавляем случайного соседа
            neighbors = [(x + dx, y + dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]
            random.shuffle(neighbors)
            
            added = False
            for neighbor in neighbors:
                if neighbor not in island_cells:
                    island_cells.add(neighbor)
                    frontier.append(neighbor)
                    added = True
                    break
            
            # Если не удалось добавить соседа, убираем клетку из границы
            if not added:
                frontier.remove(current_cell)

        return island_cells
