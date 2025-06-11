import pygame
from typing import List, Dict, Set
from ..components.transform import TransformComponent
from ..components.renderable import RenderableComponent
from ..world.game_world import GameWorld

class RenderSystem:
    """Система отрисовки игровых объектов."""
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._layer_cache: Dict[int, pygame.Surface] = {}
        self._dirty_layers: Set[int] = set()
        
    def update(self, world: GameWorld) -> None:
        """Отрисовывает все видимые сущности."""
        # Получаем все отрисовываемые сущности
        entities = world.get_entities_with_components(
            TransformComponent,
            RenderableComponent
        )
        
        # Группируем сущности по слоям
        layers: Dict[int, List[int]] = {}
        for entity in entities:
            renderable = world.get_component(entity, RenderableComponent)
            if renderable.layer not in layers:
                layers[renderable.layer] = []
            layers[renderable.layer].append(entity)
        
        # Отрисовываем каждый слой
        for layer_num in sorted(layers.keys()):
            if layer_num in self._dirty_layers or layer_num not in self._layer_cache:
                self._render_layer(world, layers[layer_num], layer_num)
            
            # Отображаем слой
            self.screen.blit(self._layer_cache[layer_num], (0, 0))
    
    def _render_layer(self, world: GameWorld, entities: List[int], layer: int) -> None:
        """Отрисовывает все сущности одного слоя."""
        # Создаем поверхность для слоя если её нет
        if layer not in self._layer_cache:
            self._layer_cache[layer] = pygame.Surface(
                self.screen.get_size(),
                pygame.SRCALPHA
            )
        
        surface = self._layer_cache[layer]
        surface.fill((0, 0, 0, 0))  # Очищаем слой
        
        # Отрисовываем каждую сущность
        for entity in entities:
            transform = world.get_component(entity, TransformComponent)
            renderable = world.get_component(entity, RenderableComponent)
            
            # Создаем поверхность с фигурой
            entity_surface = renderable.get_surface(transform.width, transform.height)
            
            # Отрисовываем на слой
            surface.blit(entity_surface, (transform.x, transform.y))
        
        self._dirty_layers.discard(layer)
        
    def invalidate_layer(self, layer: int) -> None:
        """Помечает слой как нуждающийся в перерисовке."""
        self._dirty_layers.add(layer)