import pygame
from constants.colors import BLACK

class Label:

    def __init__(self, text, x, y, size=20):
        path = "./assets/fonts/MedievalSharp-Regular.ttf"
        
        self.color = BLACK
        self.text = text
        self.pos = (x, y)
        try:
            self.font = pygame.font.Font(path, size,)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("serif", size, bold=True)
    
    def render(self, surface):
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, self.pos)