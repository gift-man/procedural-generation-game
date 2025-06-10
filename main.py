"""Пошаговая стратегия - главный файл запуска"""
import pygame
from core.game import Game

def main():
    """Запуск игры"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
