"""Система зданий игры"""
import pygame
from world.resources import ResourceType

class BuildingType:
    TOWN_HALL = "town_hall"     # Ратуша
    FARM = "farm"               # Ферма
    SAWMILL = "sawmill"         # Лесопилка
    QUARRY = "quarry"           # Каменоломня
    GOLD_MINE = "gold_mine"     # Шахта золота

class Building:
    def __init__(self, building_type, owner_id):
        self.type = building_type
        self.owner_id = owner_id

class BuildingSystem:
    def __init__(self):
        self.buildings = {}  # Словарь: (x, y) -> Building
        
        # Требования к ресурсам для строительства
        self.building_requirements = {
            BuildingType.FARM: None,                    # Любая суша
            BuildingType.SAWMILL: ResourceType.FOREST,  # Только лес
            BuildingType.QUARRY: ResourceType.STONE,    # Только камень
            BuildingType.GOLD_MINE: ResourceType.GOLD_MINE,  # Только золото
            BuildingType.TOWN_HALL: None                # Любая суша
        }
        
        # Названия зданий
        self.building_names = {
            BuildingType.FARM: "Ферма",
            BuildingType.SAWMILL: "Лесопилка", 
            BuildingType.QUARRY: "Каменоломня",
            BuildingType.GOLD_MINE: "Шахта золота",
            BuildingType.TOWN_HALL: "Ратуша"
        }

    def can_build(self, x, y, building_type, island, province_map, player_id):
        """ИСПРАВЛЕННАЯ проверка с контролем территории"""
        # Проверка 1: клетка должна быть сушей
        if not island.is_land(x, y):
            return False, "Можно строить только на суше"
        
        # Проверка 2: на клетке не должно быть другого здания
        if (x, y) in self.buildings:
            return False, "На клетке уже есть здание"
        
        # Проверка 3: клетка должна принадлежать игроку
        if (x, y) not in province_map:
            return False, "Клетка не принадлежит ни одной провинции"
        
        province_id = province_map[(x, y)]
        
        # ИСПРАВЛЕНО: СТРОГАЯ проверка принадлежности территории
        if hasattr(self, 'game') and hasattr(self.game, 'player_selection'):
            owner = self.game.player_selection.get_province_owner(province_id)
            
            if owner is None:
                return False, "Эта провинция не принадлежит ни одному игроку"
            
            if owner.player_id != player_id:
                return False, f"Эта территория принадлежит игроку {owner.name}"
            
            print(f"✅ Территориальная проверка пройдена: клетка принадлежит {owner.name}")
        else:
            return False, "Система игроков не инициализирована"
        
        # Проверка 4: соответствие ресурса требованиям здания
        required_resource = self.building_requirements[building_type]
        if required_resource is not None:
            cell_resource = island.get_resource(x, y)
            if cell_resource != required_resource:
                if hasattr(self, 'game'):
                    resource_name = self.game.island.resource_generator.get_resource_name(required_resource)
                else:
                    resource_name = required_resource
                return False, f"Для {self.building_names[building_type]} нужен {resource_name}"
        
        return True, "Можно строить"


    def build(self, x, y, building_type, owner_id, island, province_map):
        """Строит здание на клетке"""
        can_build, reason = self.can_build(x, y, building_type, island, province_map, owner_id)
        
        if not can_build:
            return False, reason
        
        # Создаем здание
        building = Building(building_type, owner_id)
        self.buildings[(x, y)] = building
        
        return True, f"{self.building_names[building_type]} построена"

    def get_building(self, x, y):
        """Возвращает здание на клетке"""
        return self.buildings.get((x, y))

    def remove_building(self, x, y):
        """Удаляет здание с клетки"""
        if (x, y) in self.buildings:
            del self.buildings[(x, y)]
            return True
        return False

    def get_player_buildings(self, player_id):
        """Возвращает все здания игрока"""
        player_buildings = {}
        for pos, building in self.buildings.items():
            if building.owner_id == player_id:
                player_buildings[pos] = building
        return player_buildings

    def assign_starting_town_hall(self, player_id, province):
        """Назначает стартовую ратушу в провинции"""
        if not province or not province['cells']:
            return False
        
        # Выбираем первую клетку провинции для ратуши
        x, y = province['cells'][0]
        
        # Строим ратушу (без проверок, так как это стартовое здание)
        building = Building(BuildingType.TOWN_HALL, player_id)
        self.buildings[(x, y)] = building
        
        return True
