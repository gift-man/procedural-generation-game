"""Точка входа в игру."""
import sys
import os

# Добавляем путь к исходникам в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

try:
    import pygame
except ImportError:
    print("Pygame не установлен!")
    print("Установите его командой:")
    print("pip install pygame>=2.6.1")
    sys.exit(1)

from src.pgg_game.core.engine import Engine

def main() -> None:
    """Точка входа в игру."""
    try:
        # Создаем движок
        engine = Engine()  # Убираем параметр world
        
        # Запускаем игру
        engine.run()
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        print("Игра завершена.")
        raise
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()