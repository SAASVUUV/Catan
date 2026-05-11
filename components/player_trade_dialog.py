import pygame
from components.modal import Modal
from components.button import Button
from core.trade import TradeOffer
from models.inventory import TRADEABLE_RESOURCES
from constants.colors import BROWN_DARK, GOLD, GRAY_STONE, GREEN_FOREST, SAND, RED_BRICK
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT

RESOURCE_COLORS = {
    ROCK: GRAY_STONE,
    TREE: GREEN_FOREST,
    LAMB: (240, 240, 240),
    BRICK: RED_BRICK,
    WHEAT: SAND
}

class PlayerTradeDialog(Modal):
    def __init__(self, proposer, all_players, on_propose, on_cancel):
        super().__init__(450, 320, "Mesa de Troca")
        self.proposer = proposer
        self.all_players = all_players
        self.on_propose = on_propose
        self.on_cancel = on_cancel

        self.offering = {r: 0 for r in TRADEABLE_RESOURCES}
        self.requesting = {r: 0 for r in TRADEABLE_RESOURCES}

        self._setup_ui()

    def _setup_ui(self):
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, 14)

        self.offer_rects = []
        self.request_rects = []
        btn_size = 40
        btn_spacing = 50
        res_start_x = self.rect.left + 50

        offer_y = self.rect.top + 70
        request_y = self.rect.top + 170

        for i, res in enumerate(TRADEABLE_RESOURCES):
            x = res_start_x + i * btn_spacing
            self.offer_rects.append({
                'rect': pygame.Rect(x, offer_y, btn_size, btn_size),
                'resource': res
            })
            self.request_rects.append({
                'rect': pygame.Rect(x, request_y, btn_size, btn_size),
                'resource': res
            })

        self.btn_propose = Button(
            self.rect.left + 50, self.rect.bottom - 55,
            130, 40, "Propor", font_size=16
        )
        self.btn_cancel = Button(
            self.rect.right - 180, self.rect.bottom - 55,
            130, 40, "Cancelar", font_size=16
        )

    def _can_propose(self) -> bool:
        has_offer = any(v > 0 for v in self.offering.values())
        has_request = any(v > 0 for v in self.requesting.values())
        if not has_offer and not has_request:
            return False
        if has_offer and not self.proposer.inventory.has_multiple(self.offering):
            return False
        return True

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            for btn_data in self.offer_rects:
                if btn_data['rect'].collidepoint(pos):
                    res = btn_data['resource']
                    max_count = self.proposer.inventory.get_count(res)
                    self.offering[res] = (self.offering[res] + 1) % (max_count + 1)
                    return True

            for btn_data in self.request_rects:
                if btn_data['rect'].collidepoint(pos):
                    res = btn_data['resource']
                    self.requesting[res] = (self.requesting[res] + 1) % 10
                    return True

            if self.btn_propose.rect.collidepoint(pos) and self._can_propose():
                offer = TradeOffer(
                    self.proposer,
                    None,
                    {r: c for r, c in self.offering.items() if c > 0},
                    {r: c for r, c in self.requesting.items() if c > 0}
                )
                self.on_propose(offer)
                return True

            if self.btn_cancel.rect.collidepoint(pos):
                self.on_cancel()
                return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            pos = event.pos
            for btn_data in self.offer_rects:
                if btn_data['rect'].collidepoint(pos):
                    res = btn_data['resource']
                    self.offering[res] = max(0, self.offering[res] - 1)
                    return True
            for btn_data in self.request_rects:
                if btn_data['rect'].collidepoint(pos):
                    res = btn_data['resource']
                    self.requesting[res] = max(0, self.requesting[res] - 1)
                    return True

        return True

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return

        super().render(surface)

        offer_label = self.font.render("Oferecer:", True, BROWN_DARK)
        surface.blit(offer_label, (self.rect.left + 30, self.rect.top + 50))

        for btn_data in self.offer_rects:
            res = btn_data['resource']
            rect = btn_data['rect']
            color = RESOURCE_COLORS.get(res, (200, 200, 200))

            pygame.draw.rect(surface, color, rect, border_radius=4)
            border_color = GOLD if self.offering[res] > 0 else BROWN_DARK
            pygame.draw.rect(surface, border_color, rect, width=2, border_radius=4)

            count_text = self.font.render(str(self.offering[res]), True, BROWN_DARK)
            surface.blit(count_text, (rect.centerx - count_text.get_width() // 2, rect.centery - count_text.get_height() // 2))

        request_label = self.font.render("Pedir:", True, BROWN_DARK)
        surface.blit(request_label, (self.rect.left + 30, self.rect.top + 150))

        for btn_data in self.request_rects:
            res = btn_data['resource']
            rect = btn_data['rect']
            color = RESOURCE_COLORS.get(res, (200, 200, 200))

            pygame.draw.rect(surface, color, rect, border_radius=4)
            border_color = GOLD if self.requesting[res] > 0 else BROWN_DARK
            pygame.draw.rect(surface, border_color, rect, width=2, border_radius=4)

            count_text = self.font.render(str(self.requesting[res]), True, BROWN_DARK)
            surface.blit(count_text, (rect.centerx - count_text.get_width() // 2, rect.centery - count_text.get_height() // 2))

        self.btn_propose.render(surface)
        self.btn_cancel.render(surface)

        if not self._can_propose():
            overlay = pygame.Surface((self.btn_propose.rect.width, self.btn_propose.rect.height), pygame.SRCALPHA)
            overlay.fill((100, 100, 100, 150))
            surface.blit(overlay, self.btn_propose.rect.topleft)


class TradeOfferDialog(Modal):
    def __init__(self, offer: TradeOffer, target, on_accept, on_reject):
        super().__init__(400, 280, f"Proposta de {offer.proposer.name}")
        self.offer = offer
        self.target = target
        self.on_accept = on_accept
        self.on_reject = on_reject

        self._setup_ui()

    def _setup_ui(self):
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, 16)

        self.btn_accept = Button(
            self.rect.left + 50, self.rect.bottom - 55,
            130, 40, "Aceitar", font_size=16
        )
        self.btn_reject = Button(
            self.rect.right - 180, self.rect.bottom - 55,
            130, 40, "Recusar", font_size=16
        )

    def _can_accept(self) -> bool:
        if not self.offer.requesting:
            return True
        return self.target.inventory.has_multiple(self.offer.requesting)

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if self.btn_accept.rect.collidepoint(pos) and self._can_accept():
                self.on_accept(self.offer, self.target)
                return True

            if self.btn_reject.rect.collidepoint(pos):
                self.on_reject()
                return True

        return True

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return

        super().render(surface)

        target_text = self.font.render(f"para {self.target.name}", True, BROWN_DARK)
        surface.blit(target_text, (self.rect.centerx - target_text.get_width() // 2, self.rect.top + 45))

        offer_y = self.rect.top + 80
        offer_text = "Oferece: "
        if not self.offer.offering:
            offer_text += "Nada"
        else:
            for res, count in self.offer.offering.items():
                offer_text += f"{self._res_name(res)} x{count}, "
            offer_text = offer_text.rstrip(", ")
        offer_surf = self.font.render(offer_text, True, BROWN_DARK)
        surface.blit(offer_surf, (self.rect.left + 30, offer_y))

        request_y = self.rect.top + 120
        request_text = "Pede: "
        if not self.offer.requesting:
            request_text += "Nada"
        else:
            for res, count in self.offer.requesting.items():
                request_text += f"{self._res_name(res)} x{count}, "
            request_text = request_text.rstrip(", ")
        request_surf = self.font.render(request_text, True, BROWN_DARK)
        surface.blit(request_surf, (self.rect.left + 30, request_y))

        self.btn_accept.render(surface)
        self.btn_reject.render(surface)

        if not self._can_accept():
            warning = self.font.render("(recursos insuficientes)", True, (180, 50, 50))
            surface.blit(warning, (self.rect.centerx - warning.get_width() // 2, self.rect.top + 160))
            overlay = pygame.Surface((self.btn_accept.rect.width, self.btn_accept.rect.height), pygame.SRCALPHA)
            overlay.fill((100, 100, 100, 150))
            surface.blit(overlay, self.btn_accept.rect.topleft)

    def _res_name(self, res: int) -> str:
        names = {ROCK: "Pedra", TREE: "Madeira", LAMB: "La", BRICK: "Tijolo", WHEAT: "Trigo"}
        return names.get(res, "?")
