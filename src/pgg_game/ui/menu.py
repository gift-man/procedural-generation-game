from typing import Callable, Dict
import pygame
from .widgets import Panel, Button, Label
from ..config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT

class MainMenu(Panel):
    """Главное меню игры."""
    def __init__(self, screen: pygame.Surface,
                 fonts: Dict[str, pygame.font.Font],
                 callbacks: Dict[str, Callable]):
        super().__init__(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.screen = screen
        self.fonts = fonts
        
        # Создаем элементы меню
        title_label = Label(
            pygame.Rect(0, SCREEN_HEIGHT // 4, SCREEN_WIDTH, 60),
            "Procedural Strategy",
            self.fonts['title'],
            COLORS['highlight']
        )
        self.add_child(title_label)
        
        # Кнопки
        button_width = 200
        button_height = 50
        button_spacing = 20
        start_y = SCREEN_HEIGHT // 2
        
        buttons = [
            ("Новая игра", callbacks.get('new_game')),
            ("Настройки", callbacks.get('settings')),
            ("Выход", callbacks.get('quit'))
        ]
        
        for i, (text, callback) in enumerate(buttons):
            button = Button(
                pygame.Rect(
                    (SCREEN_WIDTH - button_width) // 2,
                    start_y + i * (button_height + button_spacing),
                    button_width,
                    button_height
                ),
                text,
                callback,
                self.fonts['normal']
            )
            self.add_child(button)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает меню с фоном."""
        # Рисуем затемненный фон
        surface.fill(COLORS['background'])
        
        # Рисуем все элементы меню
        super().draw(surface)