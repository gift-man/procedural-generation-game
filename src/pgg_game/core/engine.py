"""Игровой движок."""
import pygame
import sys
from typing import Optional, Dict

from ..world.game_world import GameWorld
from ..systems.event_system import EventSystem
from ..systems.map_system import MapSystem
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
        try:
            # Инициализация pygame
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
            
            # Состояние игры
            self.state = GameState.MENU
            self.running = True
            
            # Фон игры
            self.background_color = (30, 40, 50)
            
            # Для подсчета FPS
            self.fps_font = pygame.font.Font(None, 24)
            self.fps_counter: Optional[pygame.Surface] = None
            
            # Подписываемся на события
            self.event_system.subscribe('start_game', self._handle_start_game)
            self.event_system.subscribe('quit_game', self._handle_quit_game)
            
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
            # Отрисовываем карту
            self.map_system.render()
            self.screen.blit(self.map_system.get_surface(), (0, 0))
        
        # Отображаем FPS если включен режим отладки
        if DEBUG['show_fps'] and self.fps_counter:
            self.screen.blit(self.fps_counter, (10, 10))

    
    def cleanup(self) -> None:
        """Освобождение ресурсов."""
        pygame.quit()
        sys.exit()