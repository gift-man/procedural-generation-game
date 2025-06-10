"""ИСПРАВЛЕННЫЕ иконки зданий БЕЗ белого фона"""
import pygame
from world.buildings import BuildingType

class BuildingIcons:
    @staticmethod
    def draw_building_icon(surface, rect, building_type, color):
        """Рисует иконку здания"""
        # ИСПРАВЛЕНО: Используем константы вместо строк
        if building_type == BuildingType.FARM:
            BuildingIcons.draw_farm(surface, rect, color)
        elif building_type == BuildingType.SAWMILL:
            BuildingIcons.draw_sawmill(surface, rect, color)
        elif building_type == BuildingType.QUARRY:
            BuildingIcons.draw_quarry(surface, rect, color)
        elif building_type == BuildingType.GOLD_MINE:
            BuildingIcons.draw_gold_mine(surface, rect, color)
        elif building_type == BuildingType.TOWN_HALL:
            BuildingIcons.draw_town_hall(surface, rect, color)

    @staticmethod
    def draw_farm(surface, rect, color):
        """Ферма - 3 горизонтальные линии (ПРОЗРАЧНАЯ)"""
        x, y = rect.topleft
        w, h = rect.size
        
        # 3 горизонтальные линии
        for i in range(3):
            y_pos = y + h * (i + 1) / 4
            start_pos = (x + w * 0.1, y_pos)
            end_pos = (x + w * 0.9, y_pos)
            pygame.draw.line(surface, color, start_pos, end_pos, 2)

    @staticmethod
    def draw_sawmill(surface, rect, color):
        """Лесопилка - 3 вертикальные линии (ПРОЗРАЧНАЯ)"""
        x, y = rect.topleft
        w, h = rect.size
        
        # 3 вертикальные линии
        for i in range(3):
            x_pos = x + w * (i + 1) / 4
            start_pos = (x_pos, y + h * 0.1)
            end_pos = (x_pos, y + h * 0.9)
            pygame.draw.line(surface, color, start_pos, end_pos, 2)

    @staticmethod
    def draw_gold_mine(surface, rect, color):
        """Шахта золота - квадрат (ПРОЗРАЧНЫЙ)"""
        # Делаем квадрат чуть меньше прямоугольника
        margin = min(rect.width, rect.height) * 0.1
        square_rect = pygame.Rect(
            rect.x + margin,
            rect.y + margin,
            rect.width - 2 * margin,
            rect.height - 2 * margin
        )
        pygame.draw.rect(surface, color, square_rect, 2)

    @staticmethod
    def draw_quarry(surface, rect, color):
        """Каменоломня - два маленьких квадрата (ПРОЗРАЧНЫЕ)"""
        x, y = rect.topleft
        w, h = rect.size
        
        # Два квадрата рядом
        square_w = w * 0.35
        square_h = h * 0.7
        margin_y = h * 0.15
        
        # Левый квадрат
        left_rect = pygame.Rect(x + w * 0.1, y + margin_y, square_w, square_h)
        pygame.draw.rect(surface, color, left_rect, 2)
        
        # Правый квадрат
        right_rect = pygame.Rect(x + w * 0.55, y + margin_y, square_w, square_h)
        pygame.draw.rect(surface, color, right_rect, 2)

    @staticmethod
    def draw_town_hall(surface, rect, color):
        """Ратуша - корона с 3 зубьями (ПРОЗРАЧНАЯ)"""
        x, y = rect.topleft
        w, h = rect.size
        
        # Основание короны
        base_y = y + h * 0.8
        pygame.draw.line(surface, color, 
                        (x + w * 0.1, base_y), 
                        (x + w * 0.9, base_y), 3)
        
        # 3 зубца короны
        # Левый зубец
        pygame.draw.lines(surface, color, False, [
            (x + w * 0.1, base_y),
            (x + w * 0.1, y + h * 0.3),
            (x + w * 0.25, y + h * 0.3),
            (x + w * 0.25, base_y)
        ], 2)
        
        # Средний зубец (выше)
        pygame.draw.lines(surface, color, False, [
            (x + w * 0.35, base_y),
            (x + w * 0.35, y + h * 0.1),
            (x + w * 0.65, y + h * 0.1),
            (x + w * 0.65, base_y)
        ], 2)
        
        # Правый зубец
        pygame.draw.lines(surface, color, False, [
            (x + w * 0.75, base_y),
            (x + w * 0.75, y + h * 0.3),
            (x + w * 0.9, y + h * 0.3),
            (x + w * 0.9, base_y)
        ], 2)
