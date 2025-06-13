"""Игровой движок."""
import pygame
import sys
from typing import Optional, Dict
from ..world.map_generator import MapGenerator
from ..world.game_world import GameWorld
from ..systems.event_system import EventSystem
from ..systems.map_system import MapSystem
from ..systems.ui_system import UISystem
from ..core.game_types import GameState
from ..config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    WINDOW_TITLE,
    COLORS,
    DEBUG
)

class Engine:
    """Основной игровой движок."""
    
    def __init__(self):
        """Инициализация движка."""
        pygame.init()
        
        # Создаем окно
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        
        # Инициализируем часы
        self.clock = pygame.time.Clock()
        
        # Создаем системы
        self.event_system = EventSystem()
        self.world = GameWorld()
        self.map_system = MapSystem()
        self.ui_system = UISystem(self.screen, self.event_system)
        
        # Состояние игры
        self.state = GameState.MENU
        self.running = True
        
        # Фон игры
        self.background_color = (30, 40, 50)  # Темно-синий фон вместо черного
        
        # Для подсчета FPS
        self.fps_font = pygame.font.Font(None, 24)
        self.fps_counter: Optional[pygame.Surface] = None
        
        # Подписываемся на события
        self.event_system.subscribe('start_game', self._handle_start_game)
        self.event_system.subscribe('open_settings', self._handle_open_settings)
        self.event_system.subscribe('quit_game', self._handle_quit_game)
      
    
        """Инициализация игрового движка."""
        try:
            # Инициализация pygame
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(WINDOW_TITLE)
            self.clock = pygame.time.Clock()
            self.running = True
            
            # Инициализация генератора карты
            self.map_generator = MapGenerator(SCREEN_WIDTH, SCREEN_HEIGHT)
            
            # Генерация карты
            if not self.map_generator.generate():
                raise RuntimeError("Не удалось сгенерировать карту")
                
        except Exception as e:
            print(f"Ошибка при инициализации движка: {e}")
            raise
    
    def run(self) -> None:
        """Главный игровой цикл."""
        try:
            while self.running:
                # Измеряем время кадра
                dt = self.clock.tick(FPS) / 1000.0
                
                # Обработка событий
                self._handle_events()
                
                # Обновление
                self._update(dt)
                
                # Отрисовка
                self._render()
                
                # Обновляем экран
                pygame.display.flip()
        except Exception as e:
            print(f"Критическая ошибка: {str(e)}")
            print("Игра завершена.")
            raise
        finally:
            self.cleanup()

    def initialize_map(self) -> None:
        """Инициализация карты."""
        try:
            self.map_generator = MapGenerator(
                width=SCREEN_WIDTH,
                height=SCREEN_HEIGHT
            )
            success = self.map_generator.generate()
            if not success:
                raise RuntimeError("Не удалось сгенерировать карту")
        except Exception as e:
            print(f"Ошибка при генерации карты: {str(e)}")
            raise    

    def _handle_events(self) -> None:
        """Обработка событий."""
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                self.running = False
            elif pygame_event.type == pygame.KEYDOWN:
                if pygame_event.key == pygame.K_ESCAPE:
                    # Переход в главное меню
                    if self.state == GameState.GAME:
                        self.state = GameState.MENU
                elif pygame_event.key == pygame.K_r and self.state == GameState.GAME:
                    # Генерация новой карты
                    self.map_system.map_generated = False
                    self.map_system.update(self.world)
            
            # Передаем событие в систему событий
            self.event_system.handle_pygame_event(pygame_event)

    def _handle_start_game(self, _: Dict) -> None:
        """Обработчик начала игры."""
        self.state = GameState.GAME
        # Сбрасываем генерацию карты при новой игре
        self.map_system.map_generated = False
        
    def _handle_open_settings(self, _: Dict) -> None:
        """Обработчик открытия настроек."""
        pass  # TODO: Реализовать окно настроек
    
    def _handle_quit_game(self, _: Dict) -> None:
        """Обработчик выхода из игры."""
        self.running = False
    
    def _update(self, dt: float) -> None:
        """
        Обновление состояния игры.
        
        Args:
            dt: Время, прошедшее с последнего кадра
        """
        # Обновляем системы
        self.map_system.update(self.world)
        self.ui_system.update(self.world, self.state)
        
        # Обновляем счетчик FPS если включен режим отладки
        if DEBUG['show_fps']:
            fps = int(self.clock.get_fps())
            self.fps_counter = self.fps_font.render(
                f'FPS: {fps}',
                True,
                COLORS['text']
            )
    
    def _render(self) -> None:
            """Отрисовка игры."""
            # Очищаем экран
            self.screen.fill(self.background_color)
            
            if self.state == GameState.GAME:
                # Отрисовываем карту только в игровом состоянии
                self.map_system.render(self.world)
                self.screen.blit(self.map_system.get_surface(), (0, 0))
            
            # Отрисовываем UI поверх всего
            self.ui_system.render(self.world, self.state)
            
            # Отображаем FPS если включен режим отладки
            if DEBUG['show_fps'] and self.fps_counter:
                self.screen.blit(self.fps_counter, (10, 10))

    
    def cleanup(self) -> None:
        """Освобождение ресурсов."""
        self.ui_system.cleanup()
        pygame.quit()
        sys.exit()