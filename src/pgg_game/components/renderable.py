from enum import Enum
from typing import Tuple, Optional
import pygame

class ShapeType(Enum):
    """Типы фигур для отрисовки."""
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    LINE = "line"
    POLYGON = "polygon"

class RenderableComponent:
    """Компонент для отрисовки объектов."""
    
    def __init__(self, 
                 shape_type: ShapeType,
                 color: Tuple[int, int, int],
                 size: Tuple[int, int] = (0, 0),
                 position: Tuple[int, int] = (0, 0),
                 filled: bool = True,
                 width: int = 1,
                 layer: int = 0):
        """
        Инициализация компонента отрисовки.

        Args:
            shape_type: Тип фигуры (из ShapeType)
            color: RGB цвет
            size: Размер (ширина, высота)
            position: Позиция (x, y)
            filled: Заполнять фигуру или нет
            width: Толщина линии для незаполненных фигур
            layer: Слой отрисовки (больше = выше)
        """
        self.shape_type = shape_type
        self.color = color
        self.size = size
        self.position = position
        self.filled = filled
        self.width = width
        self.layer = layer
        self.visible = True
        self._surface: Optional[pygame.Surface] = None
        
    def render(self, surface: pygame.Surface) -> None:
        """
        Отрисовка компонента.

        Args:
            surface: Поверхность для отрисовки
        """
        if not self.visible:
            return
            
        x, y = self.position
        width, height = self.size
        
        if self.shape_type == ShapeType.RECTANGLE:
            if self.filled:
                pygame.draw.rect(surface, self.color, (x, y, width, height))
            else:
                pygame.draw.rect(surface, self.color, (x, y, width, height), self.width)
                
        elif self.shape_type == ShapeType.CIRCLE:
            radius = min(width, height) // 2
            center = (x + radius, y + radius)
            if self.filled:
                pygame.draw.circle(surface, self.color, center, radius)
            else:
                pygame.draw.circle(surface, self.color, center, radius, self.width)
                
        elif self.shape_type == ShapeType.LINE:
            end_pos = (x + width, y + height)
            pygame.draw.line(surface, self.color, self.position, end_pos, self.width)
            
        elif self.shape_type == ShapeType.POLYGON:
            if isinstance(self._surface, list):  # Если points задан как список точек
                if self.filled:
                    pygame.draw.polygon(surface, self.color, self._surface)
                else:
                    pygame.draw.polygon(surface, self.color, self._surface, self.width)
    
    def set_points(self, points: list) -> None:
        """
        Установка точек для полигона.

        Args:
            points: Список точек [(x1, y1), (x2, y2), ...]
        """
        if self.shape_type == ShapeType.POLYGON:
            self._surface = points