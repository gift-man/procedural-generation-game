"""Отрисовка игры"""
import pygame
from core.settings import *
from graphics.colors import *

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)
    
    def draw_sea(self, island):
        """Отрисовывает море и сетку моря"""
        self.screen.fill(SEA_COLOR)
        
        for y in range(ROWS):
            for x in range(COLS):
                if not island.is_island_cell(x, y):
                    rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, SEA_GRID_COLOR, rect, 1)
    
    def draw_island(self, island):
        """Отрисовывает остров"""
        for y in range(ROWS):
            for x in range(COLS):
                if island.is_island_cell(x, y):
                    rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.screen, ISLAND_COLOR, rect)
                    pygame.draw.rect(self.screen, ISLAND_GRID_COLOR, rect, 1)
    
    def draw_island_borders(self, island):
        """Отрисовывает границы острова"""
        for y in range(ROWS):
            for x in range(COLS):
                if island.is_island_cell(x, y):
                    rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx, ny = x + dx, y + dy
                        if not island.is_island_cell(nx, ny):
                            if dx == -1:
                                pygame.draw.line(self.screen, BORDER_COLOR, rect.topleft, rect.bottomleft, BORDER_THICKNESS)
                            elif dx == 1:
                                pygame.draw.line(self.screen, BORDER_COLOR, rect.topright, rect.bottomright, BORDER_THICKNESS)
                            if dy == -1:
                                pygame.draw.line(self.screen, BORDER_COLOR, rect.topleft, rect.topright, BORDER_THICKNESS)
                            elif dy == 1:
                                pygame.draw.line(self.screen, BORDER_COLOR, rect.bottomleft, rect.bottomright, BORDER_THICKNESS)
    
    def draw_province_borders(self, island, province_map):
        """Отрисовывает границы провинций"""
        for (x, y) in island.cells:
            if (x, y) in province_map:
                rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
                current_province = province_map[(x, y)]
                
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nx, ny = x + dx, y + dy
                    neighbor = (nx, ny)
                    
                    if neighbor in province_map and province_map[neighbor] != current_province:
                        if dx == -1:
                            self.draw_thick_dashed_line(BORDER_COLOR, rect.topleft, rect.bottomleft)
                        elif dx == 1:
                            self.draw_thick_dashed_line(BORDER_COLOR, rect.topright, rect.bottomright)
                        if dy == -1:
                            self.draw_thick_dashed_line(BORDER_COLOR, rect.topleft, rect.topright)
                        elif dy == 1:
                            self.draw_thick_dashed_line(BORDER_COLOR, rect.bottomleft, rect.bottomright)
    
    def draw_ui(self):
        """Отрисовывает интерфейс"""
        text = self.font.render("SPACE - перегенерация | ESC - выход", True, TEXT_COLOR)
        self.screen.blit(text, (10, 10))
    
    def draw_thick_dashed_line(self, color, start_pos, end_pos, thickness=BORDER_THICKNESS):
        """Рисует толстую пунктирную линию"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = x2 - x1
        dy = y2 - y1
        length = (dx*dx + dy*dy) ** 0.5
        if length == 0:
            return
        dx_norm = dx / length
        dy_norm = dy / length
        current_length = 0
        while current_length < length:
            seg_start_x = x1 + dx_norm * current_length
            seg_start_y = y1 + dy_norm * current_length
            seg_end_length = min(current_length + DASH_LENGTH, length)
            seg_end_x = x1 + dx_norm * seg_end_length
            seg_end_y = y1 + dy_norm * seg_end_length
            pygame.draw.line(self.screen, color, 
                            (seg_start_x, seg_start_y), 
                            (seg_end_x, seg_end_y), thickness)
            current_length += DASH_LENGTH + GAP_LENGTH
