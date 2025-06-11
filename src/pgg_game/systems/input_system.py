"""
Система обработки пользовательского ввода.
"""
from typing import Optional
import pygame

from ..world.game_world import GameWorld
from ..systems.event_system import EventSystem, GameEvent
from ..components.selected import SelectedComponent
from ..core.game_types import GameState

class InputSystem:
    """Система обработки пользовательского ввода."""
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self._mouse_position = (0, 0)
        self._last_selected_entity: Optional[int] = None
    
    def update(self, world: GameWorld, game_state: GameState) -> None:
        """Обрабатывает все события ввода."""
        self._mouse_position = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            # Обработка выхода
            if event.type == pygame.QUIT:
                self.event_system.emit(GameEvent("quit_game", {}))
                continue
            
            # Обработка клавиатуры
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key, game_state)
            
            # Обработка мыши
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_click(event, world, game_state)
    
    def _handle_keydown(self, key: int, game_state: GameState) -> None:
        """Обрабатывает нажатия клавиш."""
        if key == pygame.K_ESCAPE:
            if game_state == GameState.GAME:
                # Переход в меню паузы
                self.event_system.emit(GameEvent(
                    "change_state",
                    {"new_state": GameState.PAUSED}
                ))
            else:
                # Выход из игры
                self.event_system.emit(GameEvent("quit_game", {}))
        
        elif key == pygame.K_RETURN:
            if game_state == GameState.MENU:
                # Начало игры
                self.event_system.emit(GameEvent(
                    "change_state",
                    {"new_state": GameState.GAME}
                ))
        
        elif key == pygame.K_SPACE:
            if game_state == GameState.GAME:
                # Завершение хода
                self.event_system.emit(GameEvent("end_turn", {}))
    
    def _handle_mouse_click(self, event: pygame.event.Event, world: GameWorld, game_state: GameState) -> None:
        """Обрабатывает клики мыши."""
        if game_state != GameState.GAME:
            return
        
        if event.button == 1:  # Левая кнопка мыши
            # Убираем предыдущее выделение
            if self._last_selected_entity is not None:
                world.remove_component(self._last_selected_entity, SelectedComponent)
            
            # Определяем, по какой провинции кликнули
            clicked_pos = event.pos
            self.event_system.emit(GameEvent(
                "province_clicked",
                {"position": clicked_pos}
            ))
        
        elif event.button == 3:  # Правая кнопка мыши
            # Отмена выделения
            if self._last_selected_entity is not None:
                world.remove_component(self._last_selected_entity, SelectedComponent)
                self._last_selected_entity = None
    
    def set_selected_entity(self, entity_id: Optional[int]) -> None:
        """Обновляет информацию о выбранной сущности."""
        self._last_selected_entity = entity_id