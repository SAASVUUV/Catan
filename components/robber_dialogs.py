import pygame

from components.button import Button
from components.modal import Modal
from constants.colors import BEIGE_MEDIUM, BROWN_DARK, GOLD
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT
from constants.types_colors import RESOURCE_COLORS
from models.inventory import TRADEABLE_RESOURCES


RESOURCE_NAMES = {
    ROCK: "Pedra",
    TREE: "Madeira",
    LAMB: "La",
    BRICK: "Tijolo",
    WHEAT: "Trigo",
}


class DiscardResourcesDialog(Modal):
    def __init__(self, player, discard_count, on_confirm):
        super().__init__(460, 330, f"{player.name}: descartar")
        self.player = player
        self.discard_count = discard_count
        self.on_confirm = on_confirm
        self.selection = {r: 0 for r in TRADEABLE_RESOURCES}

        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, 16)
        self.small_font = pygame.font.Font(caminho_fonte, 13)

        self.card_width = 56
        self.card_height = 78
        self.card_spacing = 26
        self.confirm_btn = Button(self.rect.right - 160, self.rect.bottom - 58, 120, 38, "Confirmar", font_size=16)

    def _total_selected(self):
        return sum(self.selection.values())

    def _resource_rects(self):
        total_w = len(TRADEABLE_RESOURCES) * self.card_width + (len(TRADEABLE_RESOURCES) - 1) * self.card_spacing
        start_x = self.rect.left + (self.rect.width - total_w) // 2
        y = self.rect.top + 110
        for i, resource in enumerate(TRADEABLE_RESOURCES):
            x = start_x + i * (self.card_width + self.card_spacing)
            yield resource, pygame.Rect(x, y, self.card_width, self.card_height)

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            for resource, rect in self._resource_rects():
                if rect.collidepoint(event.pos):
                    if event.button == 1:
                        available = self.player.inventory.get_count(resource)
                        if self.selection[resource] < available and self._total_selected() < self.discard_count:
                            self.selection[resource] += 1
                    elif event.button == 3:
                        self.selection[resource] = max(0, self.selection[resource] - 1)
                    return True

            if event.button == 1 and self.confirm_btn.rect.collidepoint(event.pos) and self._total_selected() == self.discard_count:
                self.on_confirm({r: c for r, c in self.selection.items() if c > 0})
                return True

        return True

    def update(self, dt: float):
        self.confirm_btn.enabled = self._total_selected() == self.discard_count
        self.confirm_btn.update()

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return

        super().render(surface)
        selected = self._total_selected()

        message = f"Escolha {self.discard_count} recurso(s) para descartar"
        message_surf = self.font.render(message, True, BROWN_DARK)
        surface.blit(message_surf, message_surf.get_rect(centerx=self.rect.centerx, top=self.rect.top + 58))

        progress = f"Selecionados: {selected}/{self.discard_count}"
        progress_surf = self.font.render(progress, True, BROWN_DARK)
        surface.blit(progress_surf, progress_surf.get_rect(centerx=self.rect.centerx, top=self.rect.top + 82))

        for resource, rect in self._resource_rects():
            color = RESOURCE_COLORS.get(resource, BEIGE_MEDIUM)
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, BROWN_DARK, rect, width=2, border_radius=6)

            count = self.player.inventory.get_count(resource)
            selected_count = self.selection[resource]
            name = self.small_font.render(RESOURCE_NAMES.get(resource, "?"), True, BROWN_DARK)
            surface.blit(name, name.get_rect(centerx=rect.centerx, top=rect.top + 6))

            count_surf = self.font.render(str(count), True, BROWN_DARK)
            surface.blit(count_surf, count_surf.get_rect(center=(rect.centerx, rect.centery + 2)))

            if selected_count:
                badge = pygame.Rect(rect.right - 22, rect.bottom - 22, 20, 20)
                pygame.draw.ellipse(surface, GOLD, badge)
                pygame.draw.ellipse(surface, BROWN_DARK, badge, width=1)
                badge_text = self.small_font.render(str(selected_count), True, BROWN_DARK)
                surface.blit(badge_text, badge_text.get_rect(center=badge.center))

        self.confirm_btn.render(surface)


class RobberStealDialog(Modal):
    def __init__(self, candidates, on_select, on_skip):
        super().__init__(380, 260, "Roubar recurso")
        self.candidates = candidates
        self.on_select = on_select
        self.on_skip = on_skip

        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, 17)
        self.buttons = []

        y = self.rect.top + 78
        for player in candidates:
            btn = Button(self.rect.left + 55, y, self.rect.width - 110, 34, player.name, font_size=15)
            self.buttons.append((player, btn))
            y += 42

        self.skip_btn = Button(self.rect.left + 110, self.rect.bottom - 52, 160, 36, "Nao roubar", font_size=15)

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for player, button in self.buttons:
                if button.handle_event(event):
                    self.on_select(player)
                    return True
            if self.skip_btn.handle_event(event):
                self.on_skip()
                return True
        return True

    def update(self, dt: float):
        for _player, button in self.buttons:
            button.update()
        self.skip_btn.update()

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return

        super().render(surface)
        info = self.font.render("Escolha um jogador adjacente", True, BROWN_DARK)
        surface.blit(info, info.get_rect(centerx=self.rect.centerx, top=self.rect.top + 48))

        for _player, button in self.buttons:
            button.render(surface)
        self.skip_btn.render(surface)
