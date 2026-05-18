import pygame
from constants import *
from .hover import Hover

class Button:
    def __init__(self, x, y, width, height, text, font_size=20, bg_image=None, shadow=False, enabled=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, font_size)
        self.hover = Hover(self.rect.collidepoint)
        self.bg_color = BLUE_MEDIUM
        self.bg_hover_color = BLUE_BRIGHT
        self.bg_disabled_color = (80, 80, 90)
        self.bg_image = pygame.transform.smoothscale(bg_image, (width, height)) if bg_image else None
        self.text_color = BEIGE_LIGHT
        self.text_hover_color = BEIGE_MEDIUM
        self.text_disabled_color = (120, 120, 120)
        self.shadow = shadow
        self.enabled = enabled
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
        if not self.enabled:
            return False
        return self.hover.handle_event(event)

    def update(self):
        if self.enabled:
            self.hover.update()

    def render(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, self.rect.topleft)
        else:
            if self.shadow:
                pygame.draw.rect(surface, self.box_shadow_color, self.shadow_rect, border_radius=6)
            if not self.enabled:
                color = self.bg_disabled_color
            elif self.hover.hovered:
                color = self.bg_color
            else:
                color = self.bg_hover_color
            pygame.draw.rect(surface, color, self.rect, border_radius=6)

        if not self.enabled:
            text_color = self.text_disabled_color
        elif self.hover.hovered:
            text_color = self.text_hover_color
        else:
            text_color = self.text_color
        label = self.font.render(self.text, True, text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))