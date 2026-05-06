import pygame
from constants.colors import BEIGE_LIGHT

class Road:

    def __init__(self, positions):
        self.x0 = positions[0][0]
        self.y0 = positions[0][1]
        self.x1 = positions[1][0]
        self.y1 = positions[1][1]
    
    def render(self, window):
        pygame.draw.line(window, BEIGE_LIGHT, (self.x0,self.y0), (self.x1,self.y1),5)
    def handle_event(self, event):
        pass
    def update(self, dt):
        pass
