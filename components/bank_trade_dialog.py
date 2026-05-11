import pygame
from components.modal import Modal
from components.button import Button
from core.trade import BankTrade
from models.inventory import TRADEABLE_RESOURCES
from constants.colors import BEIGE_MEDIUM, BROWN_DARK, GOLD, GRAY_STONE, GREEN_FOREST, SAND, RED_BRICK
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT

RESOURCE_COLORS = {
    ROCK: GRAY_STONE,
    TREE: GREEN_FOREST,
    LAMB: (240, 240, 240),
    BRICK: RED_BRICK,
    WHEAT: SAND
}

class BankTradeDialog(Modal):
    def __init__(self, player, ports, on_confirm, on_cancel):
        super().__init__(400, 320, "Trocar com Banco")
        self.player = player
        self.ports = ports
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.give_type = None
        self.receive_type = None
        self.ratio = 4

        self._setup_ui()

    def _setup_ui(self):
        btn_y_give = self.rect.top + 80
        btn_y_recv = self.rect.top + 180
        btn_size = 45
        btn_spacing = 55
        start_x = self.rect.left + 50

        self.give_buttons = []
        self.receive_buttons = []

        for i, res in enumerate(TRADEABLE_RESOURCES):
            x = start_x + i * btn_spacing
            self.give_buttons.append({
                'rect': pygame.Rect(x, btn_y_give, btn_size, btn_size),
                'resource': res
            })
            self.receive_buttons.append({
                'rect': pygame.Rect(x, btn_y_recv, btn_size, btn_size),
                'resource': res
            })

        self.btn_confirm = Button(
            self.rect.left + 50, self.rect.bottom - 55,
            130, 40, "Confirmar", font_size=16
        )
        self.btn_cancel = Button(
            self.rect.right - 180, self.rect.bottom - 55,
            130, 40, "Cancelar", font_size=16
        )

    def _update_ratio(self):
        if self.give_type is not None:
            self.ratio = BankTrade.get_ratio(self.player, self.give_type, self.ports)
        else:
            self.ratio = 4

    def _can_trade(self) -> bool:
        if self.give_type is None or self.receive_type is None:
            return False
        if self.give_type == self.receive_type:
            return False
        return self.player.inventory.has(self.give_type, self.ratio)

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            for btn_data in self.give_buttons:
                if btn_data['rect'].collidepoint(pos):
                    self.give_type = btn_data['resource']
                    self._update_ratio()
                    return True

            for btn_data in self.receive_buttons:
                if btn_data['rect'].collidepoint(pos):
                    self.receive_type = btn_data['resource']
                    return True

            if self.btn_confirm.rect.collidepoint(pos) and self._can_trade():
                self.on_confirm(self.give_type, self.ratio, self.receive_type)
                return True

            if self.btn_cancel.rect.collidepoint(pos):
                self.on_cancel()
                return True

        return True

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return

        super().render(surface)

        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        font = pygame.font.Font(caminho_fonte, 16)

        ratio_text = font.render(f"Taxa: {self.ratio}:1", True, BROWN_DARK)
        surface.blit(ratio_text, (self.rect.centerx - ratio_text.get_width() // 2, self.rect.top + 45))

        give_label = font.render("Dar:", True, BROWN_DARK)
        surface.blit(give_label, (self.rect.left + 20, self.rect.top + 60))

        for btn_data in self.give_buttons:
            res = btn_data['resource']
            rect = btn_data['rect']
            color = RESOURCE_COLORS.get(res, (200, 200, 200))

            pygame.draw.rect(surface, color, rect, border_radius=4)
            border_color = GOLD if self.give_type == res else BROWN_DARK
            border_width = 3 if self.give_type == res else 2
            pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=4)

            count = self.player.inventory.get_count(res)
            count_text = font.render(str(count), True, BROWN_DARK)
            surface.blit(count_text, (rect.centerx - count_text.get_width() // 2, rect.bottom + 2))

        recv_label = font.render("Receber:", True, BROWN_DARK)
        surface.blit(recv_label, (self.rect.left + 20, self.rect.top + 160))

        for btn_data in self.receive_buttons:
            res = btn_data['resource']
            rect = btn_data['rect']
            color = RESOURCE_COLORS.get(res, (200, 200, 200))

            pygame.draw.rect(surface, color, rect, border_radius=4)
            border_color = GOLD if self.receive_type == res else BROWN_DARK
            border_width = 3 if self.receive_type == res else 2
            pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=4)

        self.btn_confirm.render(surface)
        self.btn_cancel.render(surface)

        if not self._can_trade():
            overlay = pygame.Surface((self.btn_confirm.rect.width, self.btn_confirm.rect.height), pygame.SRCALPHA)
            overlay.fill((100, 100, 100, 150))
            surface.blit(overlay, self.btn_confirm.rect.topleft)
