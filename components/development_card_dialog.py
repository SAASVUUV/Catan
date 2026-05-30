import pygame
from components.modal import Modal
from components.button import Button
from components.card_states import CardState
from constants.colors import BROWN_DARK, BEIGE_MEDIUM
from settings import SCREEN_WIDTH, SCREEN_HEIGHT

class DevelopmentCardDialog(Modal):
    def __init__(self, player, on_cancel, on_play_card=None):
        width = int(SCREEN_WIDTH * 0.6)
        height = int(SCREEN_HEIGHT * 0.5)
        super().__init__(width, height, "Cartas de Desenvolvimento")
        self.player = player
        self.on_cancel = on_cancel
        self.on_play_card = on_play_card

        self.cards = []
        self.card_rects = []
        self._load_cards()

        btn_w, btn_h = 100, 40
        btn_x = self.x + (self.width - btn_w) // 2
        btn_y = self.y + self.height - btn_h - 20
        self.btn_close = Button(btn_x, btn_y, btn_w, btn_h, "Fechar", on_click=self.on_cancel)

        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        try:
            self.font = pygame.font.Font(caminho_fonte, 18)
            self.small_font = pygame.font.Font(caminho_fonte, 12)
        except Exception:
            self.font = pygame.font.SysFont("Arial", 18)
            self.small_font = pygame.font.SysFont("Arial", 12)

    def _load_cards(self):
        self.cards = getattr(self.player, 'development_cards', [])

    def handle_event(self, event):
        if not self.visible:
            return False
        if self.btn_close.handle_event(event):
            return True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_cancel()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.card_rects):
                if rect.collidepoint(event.pos) and i < len(self.cards):
                    card = self.cards[i]
                    if card.state == CardState.READY and self.on_play_card:
                        self.on_play_card(card)
                        return True
        return super().handle_event(event)

    def update(self, dt):
        if not self.visible:
            return
        self._load_cards()
        self.btn_close.update()

    def render(self, surface):
        if not self.visible:
            return
        super().render(surface)

        if not self.cards:
            text_surf = self.font.render("Nenhuma carta de desenvolvimento!", True, BROWN_DARK)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, self.rect.centery - 30))
            surface.blit(text_surf, text_rect)
        else:
            card_w, card_h = 80, 110
            spacing = 15
            total_width = len(self.cards) * card_w + (len(self.cards) - 1) * spacing
            start_x = self.x + (self.width - total_width) // 2
            card_y = self.y + 60

            self.card_rects = []
            for i, card in enumerate(self.cards):
                x = start_x + i * (card_w + spacing)
                rect = pygame.Rect(x, card_y, card_w, card_h)
                self.card_rects.append(rect)

                color = self._get_card_color(card)
                pygame.draw.rect(surface, color, rect, border_radius=8)
                pygame.draw.rect(surface, BROWN_DARK, rect, 2, border_radius=8)

                name_surf = self.small_font.render(card.name, True, BROWN_DARK)
                name_rect = name_surf.get_rect(centerx=rect.centerx, top=rect.top + 10)
                surface.blit(name_surf, name_rect)

                if card.state == CardState.READY:
                    status = "Pronta"
                    status_color = (0, 128, 0)
                elif card.state == CardState.LOCKED or card.bought_this_turn:
                    status = "Bloqueada"
                    status_color = (180, 0, 0)
                else:
                    status = "Usada"
                    status_color = (100, 100, 100)

                status_surf = self.small_font.render(status, True, status_color)
                status_rect = status_surf.get_rect(centerx=rect.centerx, bottom=rect.bottom - 10)
                surface.blit(status_surf, status_rect)

        self.btn_close.render(surface)

    def _get_card_color(self, card):
        from components.card_types import CardType
        if card.type == CardType.KNIGHT:
            return (100, 140, 220)
        elif card.type == CardType.VICTORY_POINT:
            return (218, 165, 32)
        elif card.type == CardType.PROGRESS:
            return (120, 180, 120)
        return BEIGE_MEDIUM
