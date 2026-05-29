import math
import pygame
from .buildable import Buildable
from utils.sprites import SpriteLoader
from utils.sound import SoundManager

MAX_ROADS = 15


class Road(Buildable):

    def __init__(self, edge):
        self.owner = None
        super().__init__()

        self.x0, self.y0 = edge[0]
        self.x1, self.y1 = edge[1]
        self._invalid_timer = 0.0
        self.house_a = None
        self.house_b = None

    def _can_place_road(self, player, all_roads=None, force_free: bool = False) -> bool:
        if self.owner is not None or not player.can_build_road(MAX_ROADS):
            return False
        if not player.is_in_setup_phase() and not force_free and not player.has_resources_for_road():
            return False
        # RN25: Estradas devem ser adjacentes a outras estruturas do mesmo jogador (exceto na fase de setup)
        if not player.is_in_setup_phase() and all_roads is not None:
            if not self._is_adjacent_to_player(player, all_roads):
                return False
        return True

    def _is_adjacent_to_player(self, player, all_roads) -> bool:
        """
        Verifica se a estrada é adjacente a:
        - Outra estrada do mesmo jogador
        - Uma casa/cidade do mesmo jogador
        """
        # Verifica se tem casa/cidade do jogador nas extremidades
        if self.house_a and self.house_a.owner is player:
            return True
        if self.house_b and self.house_b.owner is player:
            return True
        
        # Verifica se compartilha uma extremidade com outra estrada do mesmo jogador
        for road in all_roads:
            if road is None or road is self or road.owner is not player:
                continue
            # Verifica se compartilham a extremidade (x0, y0)
            if road.house_a is self.house_a or road.house_b is self.house_a:
                return True
            if road.house_a is self.house_b or road.house_b is self.house_b:
                return True
        
        return False

    def try_build(self, player, all_roads=None, force_free: bool = False) -> bool:
        if not self._can_place_road(player, all_roads, force_free=force_free):
            self._invalid_timer = 0.4
            SoundManager().play('invalid_action')
            return False

        if player.is_in_setup_phase():
            player.add_road()
        else:
            if force_free:
                if not player.can_build_road(MAX_ROADS):
                    self._invalid_timer = 0.4
                    SoundManager().play('invalid_action')
                    return False
                # place road without consuming resources
                player.add_road()
            else:
                if not player.buy_road(MAX_ROADS):
                    self._invalid_timer = 0.4
                    SoundManager().play('invalid_action')
                    return False

        self.owner = player
        self.color = player.color
        return True

    def update(self, dt):
        if self._invalid_timer > 0:
            self._invalid_timer = max(0.0, self._invalid_timer - dt)

    def render(self, surface):
        if self.owner:
            dx, dy = self.x1 - self.x0, self.y1 - self.y0
            length = int(math.hypot(dx, dy) * 1.15)

            base = SpriteLoader().get_tinted_sprite("road", self.owner.color, (16, length))
            ang = -math.degrees(math.atan2(dy, dx)) - 90
            rotated = pygame.transform.rotate(base, ang)

            cx, cy = (self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2
            rect = rotated.get_rect(center=(int(cx), int(cy)))
            surface.blit(rotated, rect.topleft)
        else:
            pygame.draw.line(surface, (180, 180, 180), (int(self.x0), int(self.y0)), (int(self.x1), int(self.y1)), 2)

        if self._invalid_timer > 0:
            pygame.draw.line(surface, (200, 40, 40), (int(self.x0), int(self.y0)), (int(self.x1), int(self.y1)), 8)

    def collidepoint(self, pos, tolerance=8):
        px, py = pos
        dx, dy = self.x1 - self.x0, self.y1 - self.y0
        length_sq = dx * dx + dy * dy
        if length_sq == 0:
            return False
        t = max(0, min(1, ((px - self.x0) * dx + (py - self.y0) * dy) / length_sq))
        return (px - (self.x0 + t * dx)) ** 2 + (py - (self.y0 + t * dy)) ** 2 <= tolerance ** 2