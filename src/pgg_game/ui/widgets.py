from typing import Optional, Callable, Tuple, List
import pygame
from ..config import COLORS

class Widget:
    """Базовый класс для всех виджетов UI."""
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.visible = True
        self.enabled = True
        self.parent = None
    
    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает виджет."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Обрабатывает событие.
        
        Returns:
            bool: True если событие обработано
        """
        return False

class Button(Widget):
    """Кнопка с текстом."""
    def __init__(self, rect: pygame.Rect, text: str, 
                 callback: Callable[[], None],
                 font: pygame.font.Font,
                 colors: Optional[dict] = None):
        super().__init__(rect)
        self.text = text
        self.callback = callback
        self.font = font
        self.colors = colors or {
            'normal': COLORS['text'],
            'hover': COLORS['highlight'],
            'disabled': COLORS['grid_lines']
        }
        self.hovered = False
        
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
            
        # Определяем цвет
        color = self.colors['disabled'] if not self.enabled else \
                self.colors['hover'] if self.hovered else \
                self.colors['normal']
        
        # Рисуем рамку
        pygame.draw.rect(surface, color, self.rect, 2)
        
        # Рисуем текст
        text_surface = self.font.render(self.text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not (self.visible and self.enabled):
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
            return self.hovered
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.callback()
                return True
        return False

class Label(Widget):
    """Текстовая метка."""
    def __init__(self, rect: pygame.Rect, text: str, 
                 font: pygame.font.Font,
                 color: Optional[pygame.Color] = None):
        super().__init__(rect)
        self.text = text
        self.font = font
        self.color = color or COLORS['text']
        
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
            
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class Panel(Widget):
    """Панель, содержащая другие виджеты."""
    def __init__(self, rect: pygame.Rect, 
                 color: Optional[pygame.Color] = None,
                 border_width: int = 0):
        super().__init__(rect)
        self.color = color or COLORS['background']
        self.border_width = border_width
        self.children: List[Widget] = []
        
    def add_child(self, widget: Widget) -> None:
        """Добавляет дочерний виджет."""
        widget.parent = self
        self.children.append(widget)
        
    def draw(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return
            
        # Рисуем панель
        pygame.draw.rect(surface, self.color, self.rect)
        if self.border_width > 0:
            pygame.draw.rect(surface, COLORS['highlight'], 
                           self.rect, self.border_width)
        
        # Рисуем дочерние виджеты
        for child in self.children:
            child.draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
            
        # Пробуем обработать событие дочерними виджетами
        for child in reversed(self.children):  # В обратном порядке для правильного перекрытия
            if child.handle_event(event):
                return True
        return False