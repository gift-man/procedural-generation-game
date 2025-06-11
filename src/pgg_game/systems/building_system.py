"""Система строительства."""
from typing import Optional, Dict, Tuple
import pygame

from ..world.game_world import GameWorld
from ..systems.event_system import EventSystem
from ..components.building import BuildingComponent, BuildingType
from ..components.resource import ResourceType, ResourceComponent
from ..components.province_info import ProvinceInfoComponent
from ..components.player import PlayerComponent

class BuildingSystem:
    """Система управления строительством."""
    
    def __init__(self, event_system: EventSystem):
        self.event_system = event_system
        self.selected_building_type: Optional[BuildingType] = None
        self.players = []  # Список игроков
        self.world: Optional[GameWorld] = None  # Ссылка на мир
        
        # Цены на здания
        self.building_costs = {
            BuildingType.FARM: 50,
            BuildingType.SAWMILL: 100,
            BuildingType.QUARRY: 150,
            BuildingType.GOLD_MINE: 200
        }

        # Производство ресурсов зданиями
        self.building_production: Dict[BuildingType, Dict[ResourceType, int]] = {
            BuildingType.FARM: {ResourceType.FOOD: 5},
            BuildingType.SAWMILL: {ResourceType.WOOD: 3},
            BuildingType.QUARRY: {ResourceType.STONE: 2},
            BuildingType.GOLD_MINE: {ResourceType.GOLD: 5}
        }
        
        # Требования к ресурсам для строительства
        self.building_requirements: Dict[BuildingType, ResourceType] = {
            BuildingType.SAWMILL: ResourceType.WOOD,
            BuildingType.QUARRY: ResourceType.STONE,
            BuildingType.GOLD_MINE: ResourceType.GOLD
        }
        
        # Подписка на события
        self.event_system.subscribe("build_selected", self._handle_build_selected)
        self.event_system.subscribe("cell_clicked", self._handle_cell_clicked)
    
    def update(self, world: GameWorld) -> None:
        """Обновление состояния системы."""
        self.world = world
    
    def _handle_build_selected(self, data: dict) -> None:
        """Обработка выбора типа здания для строительства."""
        if 'building_type' in data:
            self.selected_building_type = data['building_type']
    
    def _handle_cell_clicked(self, data: dict) -> None:
        """Обработка клика по клетке для строительства."""
        if not self.world or not self.selected_building_type or 'position' not in data:
            return
            
        position = data['position']
        province_id = data.get('province_id')
        
        if not province_id:
            return
            
        if self._can_build(self.world, province_id, position):
            self._build(self.world, province_id, position)
    
    def _can_build(
        self,
        world: GameWorld,
        province_id: int,
        position: Tuple[int, int]
    ) -> bool:
        """Проверяет возможность строительства."""
        province = world.get_component(province_id, ProvinceInfoComponent)
        if not province or position not in province.cells:
            return False
        
        # Проверяем владельца провинции
        if province.owner is None:
            return False
        
        player = world.get_component(
            self.players[province.owner],
            PlayerComponent
        )
        
        # Проверяем наличие денег
        if player.gold < self.building_costs[self.selected_building_type]:
            return False
        
        # Проверяем требования к ресурсам
        if self.selected_building_type in self.building_requirements:
            required_resource = self.building_requirements[self.selected_building_type]
            province_resources = world.get_component(province_id, ResourceComponent)
            if not province_resources.has_resource(required_resource):
                return False
        
        return True
    
    def _build(
        self,
        world: GameWorld,
        province_id: int,
        position: Tuple[int, int]
    ) -> None:
        """Строительство здания."""
        province = world.get_component(province_id, ProvinceInfoComponent)
        player = world.get_component(
            self.players[province.owner],
            PlayerComponent
        )
        
        # Создаем здание
        building_entity = world.create_entity()
        world.add_component(
            building_entity,
            BuildingComponent(
                self.selected_building_type,
                province.owner,
                position,
                self.building_production[self.selected_building_type],
                self.building_requirements.get(self.selected_building_type)
            )
        )
        
        # Списываем деньги
        player.gold -= self.building_costs[self.selected_building_type]
        
        # Добавляем здание игроку
        player.buildings.add(building_entity)