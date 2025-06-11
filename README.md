# Procedural Generation Strategy Game

Стратегическая игра с процедурной генерацией карты, написанная на Python с использованием Pygame.

## Особенности

- Процедурная генерация карты
- Пошаговая стратегия
- Система ресурсов
- Современная архитектура ECS (Entity Component System)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/gift-man/procedural-generation-game.git
cd procedural-generation-game
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Запуск

```bash
python main.py
```

## Архитектура

Проект использует архитектуру ECS (Entity Component System):

- **Entities**: Игровые объекты (провинции, игроки)
- **Components**: Данные (позиция, ресурсы, информация)
- **Systems**: Логика (рендеринг, ввод, ходы)

## Разработка

### Структура проекта
```
procedural-generation-game/
├── .gitignore           # Игнорируемые файлы
├── requirements.txt     # Зависимости проекта
├── README.md           # Документация проекта
├── main.py             # Точка входа в игру
├── assets/             # Ресурсы игры
│   ├── fonts/         # Шрифты
│   ├── images/        # Изображения
│   └── sounds/        # Звуковые эффекты
└── src/
    └── pgg_game/      # Основной пакет игры
        ├── __init__.py
        ├── config.py              # Конфигурация
        ├── components/            # Компоненты ECS
        │   ├── __init__.py
        │   ├── transform.py       # Позиция и размер
        │   ├── renderable.py      # Отображение
        │   ├── province_info.py   # Информация о провинции
        │   ├── player_info.py     # Информация об игроке
        │   ├── resource.py        # Ресурсы
        │   ├── selected.py        # Выбранные объекты
        │   └── player_input.py    # Ввод игрока
        ├── systems/               # Системы ECS
        │   ├── __init__.py
        │   ├── event_system.py    # Система событий
        │   ├── render_system.py   # Система рендеринга
        │   ├── input_system.py    # Система ввода
        │   ├── turn_system.py     # Система ходов
        │   ├── ui_system.py       # Система интерфейса
        │   └── map_system.py      # Система генерации карты
        ├── core/                  # Ядро игры
        │   ├── __init__.py
        │   ├── engine.py          # Игровой движок
        │   └── event_queue.py     # Очередь событий
        ├── ui/                    # Интерфейс
        │   ├── __init__.py
        │   ├── widgets.py         # Базовые виджеты
        │   ├── menu.py           # Главное меню
        │   └── game_ui.py        # Игровой интерфейс
        └── world/                 # Игровой мир
            ├── __init__.py
            ├── game_world.py      # Основной класс мира
            └── map_generator.py   # Генератор карты
```

## Лицензия

MIT License