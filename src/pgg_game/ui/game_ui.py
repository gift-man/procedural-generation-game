from typing import Dict, Optional
import pygame
from .widgets import Panel, Label, Button
from ..components.player_info import PlayerInfoComponent
from ..components.province_info import ProvinceInfoComponent
from ..world.game_world import GameWorld
from ..config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT

class TopPanel(Panel):
    """Верхняя панель с информацией о текущем игроке."""
    def __init__(self, rect: pygame.Rect, fonts: Dict[str, pygame.font.Font]):
        super().__init__(rect, COLORS['background'], border_width=1)
        self.fonts = fonts
        self.player_info: Optional[PlayerInfoComponent] = None
        
        # Создаем метки для информации
        self.labels = {
            'player': Label(
                pygame.Rect(10, 5, 200, 30),
                "", fonts['normal']
            ),
            'gold': Label(
                pygame.Rect(220, 5, 150, 30),
                "", fonts['normal']
            ),
            'turn': Label(
                pygame.Rect(380, 5, 150, 30),
                "", fonts['normal']
            )
        }
        
        for label in self.labels.values():
            self.add_child(label)
    
    def update(self, player: PlayerInfoComponent) -> None:
        """Обновляет информацию о игроке."""
        self.player_info = player
        if player:
            self.labels['player'].text = f"Игрок: {player.name}"
            self.labels['gold'].text = f"Золото: {player.gold}"
            self.labels['turn'].text = f"Ход: {player.turn_order}"

class ProvincePanel(Panel):
    """Панель с информацией о выбранной провинции."""
    def __init__(self, rect: pygame.Rect, fonts: Dict[str, pygame.font.Font]):
        super().__init__(rect, COLORS['background'], border_width=1)
        self.fonts = fonts
        
        # Создаем метки для информации
        self.labels = {
            'name': Label(
                pygame.Rect(10, 5, 300, 30),
                "", fonts['normal']
            ),
            'owner': Label(
                pygame.Rect(10, 35, 300, 30),
                "", fonts['normal']
            ),
            'size': Label(
                pygame.Rect(10, 65, 300, 30),
                "", fonts['normal']
            )
        }
        
        for label in self.labels.values():
            self.add_child(label)
    
    def update(self, province: ProvinceInfoComponent, 
              owner: Optional[PlayerInfoComponent] = None) -> None:
        """Обновляет информацию о провинции."""
        if province:
            self.labels['name'].text = f"Провинция: {province.name}"
            self.labels['owner'].text = f"Владелец: {owner.name if owner else 'Нейтральная'}"
            self.labels['size'].text = f"Размер: {len(province.cells)} клеток"

class GameUI:
    """Основной класс игрового интерфейса."""
    def __init__(self, screen: pygame.Surface, fonts: Dict[str, pygame.font.Font]):
        self.screen = screen
        self.fonts = fonts
        
        # Создаем панели
        self.top_panel = TopPanel(
            pygame.Rect(0, 0, SCREEN_WIDTH, 40),
            fonts
        )
        
        self.province_panel = ProvincePanel(
            pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100),
            fonts
        )
        
        self.panels = [self.top_panel, self.province_panel]
    
    def update(self, world: GameWorld, current_player_id: int,
            selected_province_id: Optional[int] = None) -> None:
        """Обновляет все элементы UI."""
        # Обновляем информацию о текущем игроке
        player = world.get_component(current_player_id, PlayerInfoComponent)
        if player:
            self.top_panel.update(player)
        
        # Обновляем информацию о выбранной провинции
        if selected_province_id is not None:
            province = world.get_component(selected_province_id, ProvinceInfoComponent)
            owner = None
            if province and province.owner is not None:
                owner = world.get_component(province.owner, PlayerInfoComponent)
            
            if province:
                self.province_panel.update(province, owner)
        
    def draw(self) -> None:
        """Отрисовывает весь интерфейс."""
        for panel in self.panels:
            panel.draw(self.screen)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Обрабатывает события UI."""
        for panel in reversed(self.panels):
            if panel.handle_event(event):
                return True
        return False