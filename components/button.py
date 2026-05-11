import pygame
from constants import *
from .hover import Hover

class Button:
    def __init__(self, x, y, width, height, text, font_size=20, bg_image=None, shadow=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, font_size)
        self.hover = Hover(self.rect.collidepoint)
        self.bg_color = BLUE_MEDIUM
        self.bg_hover_color = BLUE_BRIGHT
        self.bg_image = pygame.transform.smoothscale(bg_image, (width, height)) if bg_image else None
        self.text_color = BEIGE_LIGHT 
        self.text_hover_color = BEIGE_MEDIUM
        self.shadow = shadow
        if shadow:
            self.x_offset_shadow = -3
            self.y_offset_shadow = -5
            self.shadow_rect = pygame.Rect(
                x-self.x_offset_shadow, 
                y-self.y_offset_shadow,
                width, 
                height
            )
            self.box_shadow_color = BLACK

    def handle_event(self, event):
        return self.hover.handle_event(event)

    def update(self):
        self.hover.update()

    def render(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, self.rect.topleft)
        else:
            if self.shadow: pygame.draw.rect(surface, self.box_shadow_color, self.shadow_rect, border_radius=6)
            color = self.bg_color if self.hover.hovered else self.bg_hover_color
            pygame.draw.rect(surface, color, self.rect, border_radius=6)

        label = self.font.render(self.text, True, self.text_hover_color if self.hover.hovered else self.text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))