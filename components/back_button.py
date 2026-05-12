import pygame
from .button import Button


class BackButton(Button):
    def __init__(self, x, y, size=44):
        super().__init__(x, y, size, size, "", shadow=True)

    def render(self, surface):
        if self.shadow:
            pygame.draw.rect(surface, self.box_shadow_color, self.shadow_rect, border_radius=6)
        bg_color = self.bg_color if self.hover else self.bg_hover_color
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)

        arrow_color = self.text_hover_color if self.hover else self.text_color
        cx, cy = self.rect.centerx, self.rect.centery
        arrow_points = [
            (cx - 14, cy),
            (cx,      cy - 12),
            (cx,      cy - 5),
            (cx + 14, cy - 5),
            (cx + 14, cy + 5),
            (cx,      cy + 5),
            (cx,      cy + 12),
        ]
        pygame.draw.polygon(surface, arrow_color, arrow_points)
