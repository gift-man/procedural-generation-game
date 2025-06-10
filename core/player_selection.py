"""Система выбора провинций игроками"""
import pygame

class PlayerSelection:
    def __init__(self, player_id, color, name):
        self.player_id = player_id
        self.color = color
        self.name = name
        self.selected_province = None

class GameSelection:
    def __init__(self):
        self.players = [
            PlayerSelection(1, (255, 50, 50), "Игрок 1"),    # Красный
            PlayerSelection(2, (50, 50, 255), "Игрок 2")     # Синий
        ]
        self.current_player_index = 0
        self.selection_phase = True  # Фаза выбора провинций
        self.selections_complete = False
    
    def select_province_for_player(self, player_id, province_id):
        """Назначает провинцию конкретному игроку"""
        print(f"🔧 select_province_for_player: игрок {player_id}, провинция {province_id}")
        for player in self.players:
            if player.player_id == player_id:
                player.selected_province = province_id
                print(f"✅ Провинция {province_id} назначена игроку {player.name}")
                return True
        print(f"❌ Игрок с ID {player_id} не найден")
        return False


    def get_current_player(self):
        """Возвращает текущего игрока"""
        if self.selections_complete:
            return None
        return self.players[self.current_player_index]
    
    def select_province(self, province_id):
        """Игрок выбирает провинцию"""
        if self.selections_complete:
            return False
        
        # Проверяем, не выбрана ли уже эта провинция
        if any(p.selected_province == province_id for p in self.players):
            return False
        
        # Назначаем провинцию текущему игроку
        current_player = self.get_current_player()
        if current_player:
            current_player.selected_province = province_id
            print(f"{current_player.name} выбрал провинцию {province_id + 1}")
            
            # Переходим к следующему игроку
            self.current_player_index += 1
            
            # Проверяем, завершен ли выбор
            if self.current_player_index >= len(self.players):
                self.selections_complete = True
                self.selection_phase = False
                print("Выбор стартовых провинций завершен!")
            
            return True
        
        return False
    
    def reset_selection(self):
        """Сбрасывает выбор при перегенерации"""
        for player in self.players:
            player.selected_province = None
        self.current_player_index = 0
        self.selection_phase = True
        self.selections_complete = False
        print("Выбор провинций сброшен. Начинает Игрок 1.")
    
    def get_province_owner(self, province_id):
        """Возвращает игрока, владеющего провинцией"""
        for player in self.players:
            if player.selected_province == province_id:
                return player
        return None
    
    def is_province_selected(self, province_id):
        """Проверяет, выбрана ли провинция"""
        return any(p.selected_province == province_id for p in self.players)
