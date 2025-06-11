"""
Модуль с состояниями игры.
"""
from enum import Enum, auto

class GameState(Enum):
    """Возможные состояния игры."""
    MAIN_MENU = auto()
    GAME = auto()
    PAUSE = auto()
    OPTIONS = auto()
    EXIT = auto()