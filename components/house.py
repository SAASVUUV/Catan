import pygame
from .circle import Circle
from .buildable import Buildable


class House(Buildable):

    def __init__(self, pos, radius=10):
        self.owner = None
        super().__init__()

        self.x = pos[0]
        self.y = pos[1]
        self.level = 0

        self.circle = Circle(pos[0], pos[1], radius, (255, 0, 0))
        self.d = 5
        self._invalid_timer = 0.0
        self.adjacent_houses = set()

    def _distance_rule_violated(self):
        return any(n.owner is not None for n in self.adjacent_houses)

    def _can_place_settlement(self, player) -> bool:
        if self.owner is not None:
            return False
        if self._distance_rule_violated():
            return False
        if not player.can_build_settlement(5):
            return False

        # Valida os recursos caso não esteja no setup
        if not player.is_in_setup_phase():
            if not player.has_resources_for_settlement():
                return False
        return True

    def _can_upgrade_to_city(self, player) -> bool:
        if self.owner is not player:
            return False
        if not player.can_build_city(4):
            return False
        # Elevar a cidade sempre tem custo financeiro
        if not player.has_resources_for_city():
            return False
        return True

    def try_build(self, player) -> bool:
        # 1. Construir Aldeia (Nível 0 -> 1)
        if self.level == 0:
            if not self._can_place_settlement(player):
                self._invalid_timer = 0.4
                return False

            if player.is_in_setup_phase():
                player.add_settlement()  # Setup gratuito
            else:
                sucesso = player.buy_settlement(5)
                if not sucesso:
                    self._invalid_timer = 0.4
                    return False

            self.level = 1
            self.owner = player
            self.color = player.color
            return True

        # 2. Elevar para Cidade (Nível 1 -> 2)
        if self.level == 1 and self.owner is player:
            if not self._can_upgrade_to_city(player):
                self._invalid_timer = 0.4
                return False

            # Sempre cobrado via buy_city
            sucesso = player.buy_city(4)
            if not sucesso:
                self._invalid_timer = 0.4
                return False

            self.level = 2
            self.color = player.color
            return True

        return False

    def update(self, dt):
        if self._invalid_timer > 0:
            self._invalid_timer = max(0.0, self._invalid_timer - dt)

    def render(self, surface):
        if self.level >= 1:
            self._draw_house(surface)
        if self._invalid_timer > 0:
            pygame.draw.circle(
                surface, (200, 40, 40),
                (int(self.x), int(self.y)),
                self.circle.radius + 4, 3
            )

    def _draw_house(self, surface):
        x, y, d = self.x, self.y, self.d

        color = self.owner.color if self.owner else getattr(self, 'color', (200, 150, 100))
        r, g, b = color

        pygame.draw.rect(surface, color, (x, y, 120 // d, 100 // d))

        darker_color = (max(0, r - 30), max(0, g - 30), max(0, b - 30))

        pygame.draw.polygon(
            surface,
            darker_color,
            [
                (x - 10 // d, y),
                (x + 60 // d, y - 60 // d),
                (x + 130 // d, y),
            ]
        )

    def handle_event(self, event):
        pass