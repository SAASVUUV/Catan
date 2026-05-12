import pygame
from .circle import Circle
from .buildable import Buildable
from utils.sprites import SpriteLoader


class House(Buildable):

    def __init__(self, pos, radius=12):
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
        if self.owner is not None or self._distance_rule_violated() or not player.can_build_settlement(5):
            return False
        if not player.is_in_setup_phase() and not player.has_resources_for_settlement():
            return False
        return True

    def _can_upgrade_to_city(self, player) -> bool:
        return self.owner is player and player.can_build_city(4) and player.has_resources_for_city()

    def try_build(self, player) -> bool:
        if self.level == 0:
            if not self._can_place_settlement(player):
                self._invalid_timer = 0.4
                return False

            if player.is_in_setup_phase():
                player.add_settlement()
            else:
                if not player.buy_settlement(5):
                    self._invalid_timer = 0.4
                    return False

            self.level = 1
            self.owner = player
            self.color = player.color
            return True

        if self.level == 1 and self.owner is player:
            if not self._can_upgrade_to_city(player):
                self._invalid_timer = 0.4
                return False

            if not player.buy_city(4):
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
            pygame.draw.circle(surface, (200, 40, 40), (int(self.x), int(self.y)), self.circle.radius + 4, 3)

    def _draw_house(self, surface):
        key = "settlement" if self.level == 1 else "city"
        size = (36, 36) if self.level == 1 else (48, 48)
        c = self.owner.color if self.owner else (200, 200, 200)

        sprite = SpriteLoader().get_tinted_sprite(key, c, size)
        rect = sprite.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(sprite, rect.topleft)

    def handle_event(self, event):
        pass