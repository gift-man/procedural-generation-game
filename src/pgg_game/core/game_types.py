"""Типы данных для игры."""
from enum import Enum, auto

class GameState(Enum):
    """Состояния игры."""
    MENU = auto()
    GAME = auto()
    PAUSED = auto()
    GAME_OVER = auto()