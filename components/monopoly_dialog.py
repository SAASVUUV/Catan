import pygame
from components.modal import Modal
from constants.colors import BROWN_DARK
from constants.types_colors import RESOURCE_COLORS
from models.inventory import TRADEABLE_RESOURCES
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class MonopolyDialog(Modal):
    def __init__(self, owner, on_confirm=None, on_cancel=None, width: int = None, height: int = None, overlay_fullscreen: bool = False):
        w = width or int(SCREEN_WIDTH * 0.7)
        h = height or int(SCREEN_HEIGHT * 0.18)
        super().__init__(w, h, title="Monopólio", overlay_fullscreen=overlay_fullscreen)
        self.owner = owner
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        # position at bottom
        margin_bottom = int(SCREEN_HEIGHT * 0.06)
        self.rect.x = (SCREEN_WIDTH - self.width) // 2
        self.rect.y = SCREEN_HEIGHT - self.height - margin_bottom
        self.x, self.y = self.rect.x, self.rect.y

        self.card_width = 48
        self.card_height = 70
        self.card_spacing = 14
    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            total_w = len(TRADEABLE_RESOURCES) * (self.card_width + self.card_spacing) - self.card_spacing
            start_x = self.rect.left + (self.width - total_w) // 2
            y = self.rect.top + 40
            for i, r in enumerate(TRADEABLE_RESOURCES):
                x = start_x + i * (self.card_width + self.card_spacing)
                rect = pygame.Rect(x, y, self.card_width, self.card_height)
                if rect.collidepoint(mx, my):
                    if self.on_confirm:
                        self.on_confirm(r)
                    self.hide()
                    return True

            # cancel by clicking outside modal rect
            if not self.rect.collidepoint(mx, my):
                if self.on_cancel:
                    self.on_cancel()
                self.hide()
                return True

        return True

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        super().render(surface)
        font = pygame.font.Font(None, 20)
        total_w = len(TRADEABLE_RESOURCES) * (self.card_width + self.card_spacing) - self.card_spacing
        start_x = self.rect.left + (self.width - total_w) // 2
        y = self.rect.top + 40
        for i, r in enumerate(TRADEABLE_RESOURCES):
            x = start_x + i * (self.card_width + self.card_spacing)
            rect = pygame.Rect(x, y, self.card_width, self.card_height)
            color = RESOURCE_COLORS.get(r, (200, 200, 200))
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, BROWN_DARK, rect, width=2, border_radius=6)
            name = str(r)
            txt = font.render(name, True, BROWN_DARK)
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.bottom + 6))
