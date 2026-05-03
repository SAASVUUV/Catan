from .base_scene import BaseScene
from components.tabletop import Tabletop
import pygame
from constants.colors import BLACK

class Game(BaseScene):
    def __init__(self, manager=None):
        self.manager = manager
        self.tabletop = Tabletop(100, 100, 50)

    def handle_event(self, event: pygame.event.Event):
        pass

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        surface.fill(BLACK)
        self.tabletop.render(surface)