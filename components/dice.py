import pygame
from constants.colors import WHITE, BLACK


class Dice:
    def __init__(self, x, y, size=40):
        self.x = x
        self.y = y
        self.size = size
        self.die1 = None
        self.die2 = None
        self.visible = False
        self.dot_radius = size // 8
        self.spacing = 10

    def set_values(self, die1, die2):
        self.die1 = die1
        self.die2 = die2
        self.visible = True

    def hide(self):
        self.visible = False
        self.die1 = None
        self.die2 = None

    def _get_dot_positions(self, value, cx, cy):
        s = self.size // 4
        positions = {
            1: [(cx, cy)],
            2: [(cx - s, cy - s), (cx + s, cy + s)],
            3: [(cx - s, cy - s), (cx, cy), (cx + s, cy + s)],
            4: [(cx - s, cy - s), (cx + s, cy - s), (cx - s, cy + s), (cx + s, cy + s)],
            5: [(cx - s, cy - s), (cx + s, cy - s), (cx, cy), (cx - s, cy + s), (cx + s, cy + s)],
            6: [(cx - s, cy - s), (cx + s, cy - s), (cx - s, cy), (cx + s, cy), (cx - s, cy + s), (cx + s, cy + s)],
        }
        return positions.get(value, [])

    def _draw_die(self, surface, x, y, value):
        rect = pygame.Rect(x, y, self.size, self.size)
        pygame.draw.rect(surface, WHITE, rect, border_radius=6)
        pygame.draw.rect(surface, BLACK, rect, width=2, border_radius=6)
        cx = x + self.size // 2
        cy = y + self.size // 2
        for pos in self._get_dot_positions(value, cx, cy):
            pygame.draw.circle(surface, BLACK, pos, self.dot_radius)

    def render(self, surface):
        if not self.visible or self.die1 is None or self.die2 is None:
            return
        self._draw_die(surface, self.x, self.y, self.die1)
        self._draw_die(surface, self.x + self.size + self.spacing, self.y, self.die2)
