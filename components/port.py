import math
import pygame
from constants.types import GENERIC
from constants.colors import BROWN_WOOD
from components.circle import Circle

try:
    from utils.sprites import SpriteLoader
except ImportError:
    SpriteLoader = None


class Port:

    def __init__(self, house1, house2, type, tile_center=None):
        self.house1 = house1
        self.house2 = house2
        self.type = type
        self.ratio = 3 if type == GENERIC else 2

        mx = (self.house1.x + self.house2.x) / 2.0
        my = (self.house1.y + self.house2.y) / 2.0

        if tile_center:
            hx, hy = tile_center
            dx = mx - hx
            dy = my - hy
        else:
            cx, cy = 273.2, 250.0
            dx = mx - cx
            dy = my - cy

        dist = math.hypot(dx, dy)
        if dist == 0:
            nx, ny = 0, -1
        else:
            nx, ny = dx / dist, dy / dist

        # Afasta ligeiramente o centro do sprite para que a água fique no mar
        # e a base das pontes encoste na linha das casas. Ajuste este valor se necessário.
        distancia_mar = 18.0
        self.cx = mx + nx * distancia_mar
        self.cy = my + ny * distancia_mar

        self.x, self.y = self.cx, self.cy

        # 3. CÁLCULO DE ROTAÇÃO DO SPRITE
        self.sprite = None
        if SpriteLoader:
            try:
                loader = SpriteLoader()
                if hasattr(loader, 'get_port_sprite'):
                    base_sprite = loader.get_port_sprite(self.type, target_size=(46, 46))
                else:
                    filename = f"harbour_{'any' if type == GENERIC else type}.png"
                    base_sprite = loader.get_sprite(filename, target_size=(46, 46))

                costa_dx = self.house2.x - self.house1.x
                costa_dy = self.house2.y - self.house1.y
                angulo_rad = math.atan2(costa_dy, costa_dx)
                angulo_graus = -math.degrees(angulo_rad)

                ANGULO_BASE = 180
                angulo_final = angulo_graus + ANGULO_BASE

                self.sprite = pygame.transform.rotate(base_sprite, angulo_final)

                self.rect = self.sprite.get_rect(center=(int(self.cx), int(self.cy)))
            except Exception:
                pass

        cor_base = (50, 150, 200) if type == GENERIC else BROWN_WOOD
        self.ship = Circle(self.cx, self.cy, 12, cor_base)

    def render(self, surface):

        if self.sprite:
            surface.blit(self.sprite, self.rect.topleft)
        else:
            self.ship.render(surface)