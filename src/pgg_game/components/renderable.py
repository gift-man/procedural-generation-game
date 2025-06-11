"""Компонент для отображаемых объектов."""
from typing import Tuple, Optional
import pygame

class RenderableComponent:
    """Компонент для объектов, которые можно отрисовать."""
    
    def __init__(
        self,
        color: Tuple[int, int, int],
        width: int,
        height: int,
        alpha: int = 255,
        border_width: int = 0,
        border_color: Optional[Tuple[int, int, int]] = None,
        layer: int = 0
    ):
        """
        Инициализация компонента отрисовки.

        Args:
            color: RGB цвет заливки
            width: Ширина объекта
            height: Высота объекта
            alpha: Прозрачность (0-255)
            border_width: Толщина границы
            border_color: RGB цвет границы
            layer: Слой отрисовки (чем больше, тем выше)
        """
        self.color = color
        self.width = width
        self.height = height
        self.alpha = alpha
        self.border_width = border_width
        self.border_color = border_color
        self.layer = layer
        
        # Создаем поверхность для отрисовки
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Заливаем основным цветом
        pygame.draw.rect(
            self.surface,
            (*color, alpha),
            pygame.Rect(0, 0, width, height)
        )
        
        # Если есть граница, рисуем её
        if border_width > 0 and border_color is not None:
            pygame.draw.rect(
                self.surface,
                (*border_color, alpha),
                pygame.Rect(0, 0, width, height),
                border_width
            )
    
    def update_color(self, color: Tuple[int, int, int]) -> None:
        """
        Обновляет цвет объекта.

        Args:
            color: Новый RGB цвет
        """
        self.color = color
        # Перерисовываем поверхность
        self.surface.fill((*color, self.alpha))
        # Если есть граница, перерисовываем её
        if self.border_width > 0 and self.border_color is not None:
            pygame.draw.rect(
                self.surface,
                (*self.border_color, self.alpha),
                pygame.Rect(0, 0, self.width, self.height),
                self.border_width
            )
    
    def set_alpha(self, alpha: int) -> None:
        """
        Устанавливает прозрачность объекта.

        Args:
            alpha: Значение прозрачности (0-255)
        """
        self.alpha = max(0, min(255, alpha))
        self.surface.set_alpha(self.alpha)
    
    def get_rect(self) -> pygame.Rect:
        """
        Получает прямоугольник объекта.

        Returns:
            pygame.Rect: Прямоугольник объекта
        """
        return self.surface.get_rect()