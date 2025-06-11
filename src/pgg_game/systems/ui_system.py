"""
Система пользовательского интерфейса.
Отвечает за отображение всех UI элементов игры.
"""
import pygame
from typing import Dict, Optional, List, Tuple
from enum import Enum

from ..world.game_world import GameWorld
from ..systems.event_system import EventSystem
from ..core.game_types import GameState
from ..config import (
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    COLORS,
    GAME_CONFIG,
    UI_CONFIG
)

class UIElement(Enum):
    """Типы UI элементов."""
    BUTTON = "button"
    LABEL = "label"
    PANEL = "panel"

class UISystem:
    """Система управления пользовательским интерфейсом."""
    
    def __init__(self, screen: pygame.Surface, event_system: EventSystem):
        """
        Инициализация системы UI.
        
        Args:
            screen: Поверхность для отрисовки
            event_system: Система событий
        """
        self.screen = screen
        self.event_system = event_system
        
        # Инициализация шрифтов
        self._init_fonts()
        
        # Состояние UI
        self.selected_province = None
        self.hovering_province = None
        self.message_queue: List[Tuple[str, float]] = []
        self.selected_menu_item = 0
        
        # Кэширование поверхностей
        self._cached_surfaces: Dict[str, pygame.Surface] = {}
        
        # Слой для UI
        self.ui_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Информация об игроке
        self.player_gold = GAME_CONFIG['starting_gold']
        self.current_turn = 1
        
        # Настройки меню
        self.menu_items = ['Новая игра', 'Настройки', 'Выход']
        self.button_states = {item: False for item in self.menu_items}
        
        # Подписка на события
        self.event_system.subscribe('mouse_motion', self._handle_mouse_motion)
        self.event_system.subscribe('mouse_click', self._handle_mouse_click)
        self.event_system.subscribe('key_down', self._handle_key_down)
    
    def _init_fonts(self) -> None:
        """Инициализация шрифтов."""
        pygame.font.init()
        try:
            self.title_font = pygame.font.Font(None, 48)
            self.menu_font = pygame.font.Font(None, 36)
            self.info_font = pygame.font.Font(None, 24)
        except pygame.error:
            print("Ошибка загрузки шрифтов. Используем системные шрифты.")
            self.title_font = pygame.font.SysFont('Arial', 48)
            self.menu_font = pygame.font.SysFont('Arial', 36)
            self.info_font = pygame.font.SysFont('Arial', 24)
    
    def _handle_key_down(self, event_data: Dict) -> None:
        """
        Обработка нажатия клавиши.
        
        Args:
            event_data: Данные события
        """
        key = event_data.get('key')
        if key == pygame.K_UP:
            self.selected_menu_item = (self.selected_menu_item - 1) % len(self.menu_items)
        elif key == pygame.K_DOWN:
            self.selected_menu_item = (self.selected_menu_item + 1) % len(self.menu_items)
        elif key == pygame.K_RETURN:
            self._handle_menu_selection()
    
    def _handle_menu_selection(self) -> None:
        """Обработка выбора пункта меню."""
        selected_item = self.menu_items[self.selected_menu_item].lower()
        
        if selected_item == 'новая игра':
            self.event_system.emit('start_game', {})
        elif selected_item == 'настройки':
            self.event_system.emit('open_settings', {})
        elif selected_item == 'выход':
            self.event_system.emit('quit_game', {})
    
    def update(self, world: GameWorld, game_state: GameState) -> None:
        """
        Обновление состояния UI.
        
        Args:
            world: Игровой мир
            game_state: Текущее состояние игры
        """
        # Очищаем слой UI
        self.ui_layer.fill((0, 0, 0, 0))
        
        # Обновляем очередь сообщений
        current_time = pygame.time.get_ticks() / 1000.0
        self.message_queue = [
            (msg, time) for msg, time in self.message_queue
            if current_time < time
        ]
    
    def render(self, world: GameWorld, game_state: GameState) -> None:
        """
        Отрисовка UI в зависимости от состояния игры.
        
        Args:
            world: Игровой мир
            game_state: Текущее состояние игры
        """
        if game_state == GameState.MENU:
            self._render_menu()
        elif game_state == GameState.GAME:
            self._render_game_ui(world)
        elif game_state == GameState.PAUSED:
            self._render_pause_menu()
        
        # Отображаем сообщения
        self._render_messages()
        
        # Отображаем UI слой
        self.screen.blit(self.ui_layer, (0, 0))
    
    def _render_menu(self) -> None:
        """Отрисовка главного меню."""
        # Заголовок
        title_text = "Процедурная Генерация Игры"
        title_surface = self.title_font.render(title_text, True, COLORS['text'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.ui_layer.blit(title_surface, title_rect)
        
        # Кнопки меню
        button_y = SCREEN_HEIGHT // 2
        for i, item in enumerate(self.menu_items):
            button_color = COLORS['ui_button_hover'] if i == self.selected_menu_item else COLORS['ui_button']
            text_color = COLORS['text_highlighted'] if i == self.selected_menu_item else COLORS['text']
            
            # Создаем кнопку
            button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 100,
                button_y + i * 60,
                200,
                50
            )
            
            # Отрисовка фона кнопки
            pygame.draw.rect(self.ui_layer, button_color, button_rect)
            pygame.draw.rect(self.ui_layer, COLORS['ui_border'], button_rect, 2)
            
            # Отрисовка текста
            text_surface = self.menu_font.render(item, True, text_color)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.ui_layer.blit(text_surface, text_rect)
    
    def _render_game_ui(self, world: GameWorld) -> None:
        """
        Отрисовка игрового интерфейса.
        
        Args:
            world: Игровой мир
        """
        # Отрисовываем подсказки управления
        hints = [
            "ESC - Вернуться в меню",
            "R - Создать новую карту"
        ]
        
        y_offset = 10
        for hint in hints:
            hint_surface = self.info_font.render(hint, True, COLORS['text'])
            hint_rect = hint_surface.get_rect(topright=(SCREEN_WIDTH - 10, y_offset))
            self.ui_layer.blit(hint_surface, hint_rect)
            y_offset += 25
    
    def _render_pause_menu(self) -> None:
        """Отрисовка меню паузы."""
        # Затемнение фона
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(COLORS['background'])
        overlay.set_alpha(128)
        self.ui_layer.blit(overlay, (0, 0))
        
        # Заголовок
        title_text = "Пауза"
        title_surface = self.title_font.render(title_text, True, COLORS['text'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.ui_layer.blit(title_surface, title_rect)
    
    def _render_resource_panel(self) -> None:
        """Отрисовка панели ресурсов."""
        panel_height = 30
        panel_width = 200
        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel.fill((*COLORS['ui_background'], 200))
        
        # Отображение золота
        gold_text = f"Золото: {self.player_gold}"
        gold_surface = self.info_font.render(gold_text, True, COLORS['text'])
        panel.blit(gold_surface, (10, 5))
        
        self.ui_layer.blit(panel, (10, 10))
    
    def _handle_mouse_motion(self, event_data: Dict) -> None:
        """
        Обработка движения мыши.
        
        Args:
            event_data: Данные события
        """
        mouse_pos = event_data.get('pos')
        if not mouse_pos:
            return
            
        # Проверяем наведение на кнопки меню
        button_y = SCREEN_HEIGHT // 2
        for i, item in enumerate(self.menu_items):
            button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 100,
                button_y + i * 60,
                200,
                50
            )
            if button_rect.collidepoint(mouse_pos):
                self.selected_menu_item = i
                break
    
    def _handle_mouse_click(self, event_data: Dict) -> None:
        """
        Обработка клика мыши.
        
        Args:
            event_data: Данные события
        """
        mouse_pos = event_data.get('pos')
        if not mouse_pos:
            return
            
        # Обработка кликов по кнопкам меню
        button_y = SCREEN_HEIGHT // 2
        for i, item in enumerate(self.menu_items):
            button_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 100,
                button_y + i * 60,
                200,
                50
            )
            if button_rect.collidepoint(mouse_pos):
                self.selected_menu_item = i
                self._handle_menu_selection()
                break
    
    def _render_messages(self) -> None:
        """Отрисовка очереди сообщений."""
        y_offset = SCREEN_HEIGHT - 60
        for message, _ in self.message_queue:
            text_surface = self.info_font.render(message, True, COLORS['text'])
            self.ui_layer.blit(text_surface, (10, y_offset))
            y_offset -= 25
    
    def add_message(self, message: str, duration: float = 3.0) -> None:
        """
        Добавляет сообщение в очередь.
        
        Args:
            message: Текст сообщения
            duration: Продолжительность показа в секундах
        """
        current_time = pygame.time.get_ticks() / 1000.0
        self.message_queue.append((message, current_time + duration))
    
    def cleanup(self) -> None:
        """Освобождает ресурсы."""
        self._cached_surfaces.clear()