import pygame
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, font_size=20, bg_image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_offset_shadow = -3
        self.y_offset_shadow = -5
        self.shadow_rect = pygame.Rect(
            x-self.x_offset_shadow, 
            y-self.y_offset_shadow,
            width, 
            height
        )
        self.text = text
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, font_size)
        self.hovered = False
        self.mouse_in = False
        self.bg_color = BLUE_MEDIUM
        self.bg_hover_color = BLUE_BRIGHT
        self.box_shadow_color = BLACK
        self.bg_image = pygame.transform.smoothscale(bg_image, (width, height)) if bg_image else None
        self.text_color = BEIGE_LIGHT 
        self.text_hover_color = BEIGE_MEDIUM

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse_in = True if self.hovered else False
            self.hovered = self.rect.collidepoint(event.pos)
            if(self.hovered and self.mouse_in): self.cursor_hover()
            elif(not self.hovered and self.mouse_in): self.cursor_default()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def cursor_hover(self): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    def cursor_default(self): pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def update(self):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())

    def render(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, self.rect.topleft)
        else:
            color = self.bg_color if self.hovered else self.bg_hover_color
            pygame.draw.rect(surface, self.box_shadow_color, self.shadow_rect)
            pygame.draw.rect(surface, color, self.rect, border_radius=6)


        label = self.font.render(self.text, True, self.text_hover_color if self.hovered else self.text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))