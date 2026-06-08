import pygame
from utils.resources import resource_path

class Text:

    def __init__(self, text, font_size, color, pos):
        self.text = text
        self.font_size = font_size
        self.color = color
        caminho_fonte = resource_path('assets', 'fonts', 'MedievalSharp-Regular.ttf')
        self.font = pygame.font.Font(caminho_fonte, font_size)
        self.pos = pos

    def render(self, surface):
        label = self.font.render(self.text, True, self.color)
        surface.blit(label, label.get_rect(self.pos))
    
    def render_center(self, surface):
        label = self.font.render(self.text, True, self.color)
        surface.blit(label, label.get_rect(center=self.pos))