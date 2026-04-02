import pygame

class Button:
    def __init__(self, x, y, width, height, text, font_size=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.SysFont("Arial", font_size)
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = (255, 255, 255)
        self.hovered = False
 
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False
 
    def update(self):
        self.hovered = self.rect.collidepoint(pygame.mouse.get_pos())
 
    def render(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (180, 180, 180), self.rect, width=1, border_radius=6)
        label = self.font.render(self.text, True, self.text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))
 