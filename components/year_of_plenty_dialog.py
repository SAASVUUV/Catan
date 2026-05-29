import pygame
from components.modal import Modal
from components.button import Button
from constants.colors import BROWN_DARK, BEIGE_LIGHT, GREEN_FOREST, YELLOW
from constants.types_colors import RESOURCE_COLORS
from models.inventory import TRADEABLE_RESOURCES
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class YearOfPlentyDialog(Modal):
    def __init__(self, owner, bank, on_confirm=None, on_cancel=None, width: int = None, height: int = None, overlay_fullscreen: bool = False):
        # compute responsive size if not provided
        w = width or int(SCREEN_WIDTH * 0.8)
        h = height or int(SCREEN_HEIGHT * 0.22)
        super().__init__(w, h, title="Ano de Fartura", overlay_fullscreen=overlay_fullscreen)
        self.owner = owner
        self.bank = bank
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        margin_bottom = int(SCREEN_HEIGHT * 0.05)
        self.rect.x = (SCREEN_WIDTH - self.width) // 2
        self.rect.y = SCREEN_HEIGHT - self.height - margin_bottom
        self.x, self.y = self.rect.x, self.rect.y

        self.card_width = 44
        self.card_height = 66
        self.card_spacing = 12

        # selection counts per resource
        self.selection = {r: 0 for r in TRADEABLE_RESOURCES}

        # buttons
        bx = self.rect.left + 20
        by = self.rect.bottom - 48
        self.confirm_btn = Button(bx + self.width - 140, by, 120, 36, "Confirmar")
        self.cancel_btn = Button(bx + 10, by, 100, 36, "Cancelar")
    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # buttons
            if self.cancel_btn.handle_event(event):
                if self.on_cancel:
                    self.on_cancel()
                self.hide()
                return True
            if self.confirm_btn.handle_event(event) and self._total_selected() == 2:
                self._do_confirm()
                return True

            # check resource clicks inside modal
            mx, my = event.pos
            padding = 20
            total_w = len(TRADEABLE_RESOURCES) * (self.card_width + self.card_spacing) - self.card_spacing
            start_x = self.rect.left + (self.width - total_w) // 2
            y = self.rect.top + 50
            for i, r in enumerate(TRADEABLE_RESOURCES):
                x = start_x + i * (self.card_width + self.card_spacing)
                rect = pygame.Rect(x, y, self.card_width, self.card_height)
                if rect.collidepoint(mx, my):
                    # allow selection only if bank has enough for the new count
                    if self.selection[r] < self.bank.get_count(r):
                        if self._total_selected() < 2:
                            self.selection[r] += 1
                    else:
                        # cannot select this resource (no bank stock)
                        pass
                    return True

        return True

    def _total_selected(self):
        return sum(self.selection.values())

    def _do_confirm(self):
        resources = []
        for r, cnt in self.selection.items():
            resources.extend([r] * cnt)
        if len(resources) != 2:
            return
        if self.on_confirm:
            self.on_confirm(resources)
        self.hide()


    def update(self, dt: float):
        # enable confirm only when exactly 2 selected
        self.confirm_btn.enabled = (self._total_selected() == 2)
        self.confirm_btn.update()
        self.cancel_btn.update()

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        super().render(surface)

        # draw resource cards
        total_w = len(TRADEABLE_RESOURCES) * (self.card_width + self.card_spacing) - self.card_spacing
        start_x = self.rect.left + (self.width - total_w) // 2
        y = self.rect.top + 50
        font = pygame.font.Font(None, 20)

        for i, r in enumerate(TRADEABLE_RESOURCES):
            x = start_x + i * (self.card_width + self.card_spacing)
            rect = pygame.Rect(x, y, self.card_width, self.card_height)
            color = RESOURCE_COLORS.get(r, (200, 200, 200))
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, BROWN_DARK, rect, width=2, border_radius=6)

            # bank count
            count = self.bank.get_count(r)
            count_surf = font.render(str(count), True, BROWN_DARK)
            surface.blit(count_surf, (x + 6, y + 6))

            # selected overlay
            sel = self.selection.get(r, 0)
            if sel > 0:
                sel_surf = font.render(str(sel), True, BEIGE_LIGHT)
                sel_rect = sel_surf.get_rect(center=(rect.centerx, rect.bottom - 12))
                pygame.draw.circle(surface, GREEN_FOREST, sel_rect.center, 12)
                surface.blit(sel_surf, sel_rect)

        # selection status
        status_font = pygame.font.Font(None, 24)
        status = f"Selecionados: {self._total_selected()}/2"
        status_surf = status_font.render(status, True, BROWN_DARK)
        surface.blit(status_surf, (self.rect.left + 20, self.rect.top + 20))

        # buttons
        self.confirm_btn.render(surface)
        self.cancel_btn.render(surface)
