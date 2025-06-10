"""
Класс провинции
"""

class Province:
    def __init__(self, province_id, cells):
        self.id = province_id
        self.cells = cells
        self.size = len(cells)
    
    def add_cell(self, cell):
        """Добавляет клетку к провинции"""
        if cell not in self.cells:
            self.cells.append(cell)
            self.size = len(self.cells)
    
    def remove_cell(self, cell):
        """Удаляет клетку из провинции"""
        if cell in self.cells:
            self.cells.remove(cell)
            self.size = len(self.cells)
    
    def get_neighbors(self):
        """Возвращает всех соседей провинции"""
        neighbors = set()
        for x, y in self.cells:
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                neighbors.add((x+dx, y+dy))
        return neighbors - set(self.cells)
    
    def __str__(self):
        return f"Province {self.id}: {self.size} cells"
