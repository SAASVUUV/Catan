import pygame
from constants import colors as C
from .hover import Hover

def draw_person_icon(surface, cx, cy, size, color):
    r = size // 5
    pygame.draw.circle(surface, color, (cx, cy - size // 3), r)
    body_rect = pygame.Rect(cx - r, cy - size // 8, r * 2, size // 2)
    pygame.draw.rect(surface, color, body_rect, border_radius=r)


def draw_bot_icon(surface, cx, cy, size, color):
    hw, hh = size // 3, size // 4
    head = pygame.Rect(cx - hw, cy - size // 2, hw * 2, hh)
    pygame.draw.rect(surface, color, head, border_radius=4)
    ey = cy - size // 2 + hh // 2
    pygame.draw.circle(surface, C.ICON_DOT, (cx - hw // 3, ey), 3)
    pygame.draw.circle(surface, C.ICON_DOT, (cx + hw // 3, ey), 3)
    pygame.draw.line(surface, color, (cx, cy - size // 2), (cx, cy - size // 2 - 8), 2)
    pygame.draw.circle(surface, color, (cx, cy - size // 2 - 10), 3)
    bw, bh = size // 2, size // 3
    body = pygame.Rect(cx - bw // 2, cy - size // 2 + hh + 4, bw, bh)
    pygame.draw.rect(surface, color, body, border_radius=4)


class PlayerSlot:
    SIZE = 72

    def __init__(self, x, y, index):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.index = index
        self.is_bot = (index == 3)
        self.font = pygame.font.SysFont("Arial", 11)
        self.hover = Hover(self.rect.collidepoint, on_mouse_click=self.on_mouse_click)
        self.hovered = False
        self.mouse_in = False
    
    def on_mouse_click(self):
        self.is_bot = not self.is_bot

    def handle_event(self, event):
        return self.hover.handle_event(event)

    def update(self):
        self.hover.update()

    def _background_color(self):
        return C.SLOT_BG_HOVER if self.hover.hovered else C.SLOT_BG

    def _border_color(self):
        return C.SLOT_BORDER_BOT if self.is_bot else C.SLOT_BORDER_PLAYER

    def _icon_color(self):
        return C.ICON_BOT if self.is_bot else C.ICON_PLAYER

    def _label_text(self):
        return "BOT" if self.is_bot else f"P{self.index + 1}"

    def render(self, surface):
        pygame.draw.rect(surface, self._background_color(), self.rect, border_radius=10)
        pygame.draw.rect(surface, self._border_color(), self.rect, 2, border_radius=10)

        cx, cy = self.rect.centerx, self.rect.centery - 6
        if self.is_bot:
            draw_bot_icon(surface, cx, cy, 44, self._icon_color())
        else:
            draw_person_icon(surface, cx, cy, 44, self._icon_color())

        label = self._label_text()
        txt = self.font.render(label, True, self._icon_color())
        surface.blit(txt, txt.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 4))
