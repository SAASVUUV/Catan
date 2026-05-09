import pygame
from .circle import Circle

class House:

    def __init__(self, pos, color=(0,0,0), radius=10):
        self.x = pos[0]
        self.y = pos[1]
        # lvl 0 não construída
        # lvl 1 vila
        # lvl 2 cidade
        self.level = 1
        self.circle = Circle(pos[0], pos[1], radius, (255,0,0))
        self.d = 5
        self.owner = None

    def render(self, surface):
        if(self.level == 1):
            self.draw_house(surface, self.x, self.y)
        if(self.level == 2):
            self.draw_house(surface, self.x, self.y)

    def draw_house(self, surface, x, y):
        pygame.draw.rect(surface, (200/self.d, 150/self.d, 100/self.d), (x, y, 120/self.d, 100/self.d))
        pygame.draw.polygon(
            surface,
            (150/self.d, 50/self.d, 50/self.d),
            [
                (x - 10/self.d, y),
                (x + 60/self.d, y - 60/self.d),
                (x + 130/self.d, y)
            ]
        )
    def handle_event(self, event):
        pass
    def update(self, dt):
        pass