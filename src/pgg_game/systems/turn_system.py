"""Система управления ходами."""
from enum import Enum, auto
from typing import Optional, List, Tuple
import pygame

from ..world.game_world import GameWorld
from ..systems.event_system import EventSystem
from ..components.player import PlayerComponent
from ..components.province_info import ProvinceInfoComponent
from ..components.building import BuildingComponent, BuildingType
from ..components.resource import ResourceType
from ..config import COLORS

class TurnPhase(Enum):
    """Фазы хода."""
    PROVINCE_SELECTION = auto()  # Выбор начальной провинции
    TOWN_HALL_PLACEMENT = auto() # Размещение ратуши
    NORMAL_TURN = auto()         # Обычный ход
    GAME_OVER = auto()           # Игра окончена

class TurnSystem:
    """Система управления ходами."""
    
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.current_player = 0
        self.phase = TurnPhase.PROVINCE_SELECTION
        self.players: List[int] = []  # ID сущностей игроков
        self.selected_province: Optional[int] = None
        self.world: Optional[GameWorld] = None
        
        # Цены на здания
        self.building_costs = {
            BuildingType.FARM: 50,
            BuildingType.SAWMILL: 100,
            BuildingType.QUARRY: 150,
            BuildingType.GOLD_MINE: 200
        }
        
        # Подписываемся на события
        self.event_system.subscribe("province_clicked", self._handle_province_click)
        self.event_system.subscribe("cell_clicked", self._handle_cell_click)
        self.event_system.subscribe("end_turn", self._handle_end_turn)
    
    def update(self, world: GameWorld) -> None:
        """Обновление системы."""
        self.world = world  # Сохраняем ссылку на мир
        if not self.players:
            self._init_players(world)
            
        self._update_resources()  # Убираем параметр world
    
    def _init_players(self, world: GameWorld) -> None:
        """Инициализация игроков."""
        # Создаем двух игроков
        for i, color in enumerate([
            COLORS['player_one'],
            COLORS['player_two']
        ]):
            player_entity = world.create_entity()
            world.add_component(
                player_entity,
                PlayerComponent(i, color)
            )
            self.players.append(player_entity)
    
    def _handle_province_click(self, data: dict) -> None:
        """Обработка клика по провинции."""
        if 'province_id' not in data:
            return
            
        province_id = data['province_id']
        
        if self.phase == TurnPhase.PROVINCE_SELECTION:
            self._handle_province_selection(province_id)
        elif self.phase == TurnPhase.NORMAL_TURN:
            self._handle_normal_turn_province_click(province_id)
    
    def _handle_cell_click(self, data: dict) -> None:
        """Обработка клика по клетке."""
        if self.phase == TurnPhase.TOWN_HALL_PLACEMENT:
            self._handle_town_hall_placement(data)
    
    def _handle_end_turn(self, data: dict) -> None:
        """Обработка конца хода."""
        if self.phase == TurnPhase.NORMAL_TURN:
            self._next_player_or_phase()
    
    def _handle_normal_turn_province_click(self, province_id: int) -> None:
        """Обработка клика по провинции в обычном режиме."""
        if not self.world:
            return
            
        province = self.world.get_component(province_id, ProvinceInfoComponent)
        if province and province.owner == self.current_player:
            self.selected_province = province_id
    
    def _handle_province_selection(self, province_id: int) -> None:
        """Обработка выбора начальной провинции."""
        if not self.world:
            return
            
        # Проверяем, что провинция не занята
        province = self.world.get_component(province_id, ProvinceInfoComponent)
        if province and province.owner is None:
            # Захватываем провинцию
            province.owner = self.current_player
            player = self.world.get_component(
                self.players[self.current_player],
                PlayerComponent
            )
            player.provinces.add(province_id)
            
            # Переходим к размещению ратуши
            self.phase = TurnPhase.TOWN_HALL_PLACEMENT
            self.selected_province = province_id
    
    def _handle_town_hall_placement(self, data: dict) -> None:
        """Обработка размещения ратуши."""
        if not self.world or not data.get('position'):
            return
            
        position = data['position']
        province = self.world.get_component(
            self.selected_province,
            ProvinceInfoComponent
        )
        
        if position in province.cells:
            # Создаем ратушу
            building_entity = self.world.create_entity()
            self.world.add_component(
                building_entity,
                BuildingComponent(
                    BuildingType.TOWN_HALL,
                    self.current_player,
                    position,
                    {ResourceType.GOLD: 10}  # Базовый доход от ратуши
                )
            )
            
            province.has_town_hall = True
            province.town_hall_position = position
            
            # Помечаем, что игрок разместил ратушу
            player = self.world.get_component(
                self.players[self.current_player],
                PlayerComponent
            )
            player.has_placed_town_hall = True
            
            # Переходим к следующему игроку или фазе
            self._next_player_or_phase()
    
    def _next_player_or_phase(self) -> None:
        """Переход к следующему игроку или фазе."""
        if not self.world:
            return
            
        self.current_player = (self.current_player + 1) % len(self.players)
        
        # Если все игроки разместили ратуши
        if self.current_player == 0 and all(
            self.world.get_component(player_id, PlayerComponent).has_placed_town_hall
            for player_id in self.players
        ):
            self.phase = TurnPhase.NORMAL_TURN
        
        self.selected_province = None
    
    def _update_resources(self) -> None:
        """Обновление ресурсов в конце хода."""
        if not self.world or self.phase != TurnPhase.NORMAL_TURN:
            return
            
        for player_id in self.players:
            player = self.world.get_component(player_id, PlayerComponent)
            
            # Собираем ресурсы со всех зданий
            for building_id in player.buildings:
                building = self.world.get_component(building_id, BuildingComponent)
                for resource_type, amount in building.production_per_turn.items():
                    player.resources[resource_type] = (
                        player.resources.get(resource_type, 0) + amount
                    )