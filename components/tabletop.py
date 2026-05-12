from .hexagon_tile import HexagonTile
from .port import Port
from constants.types import *
from math import cos, pi, sqrt
from utils.myrandom import takesome
from utils.sprites import SpriteLoader
import pygame

class Tabletop:

    def __init__(self, x0, y0, hex_radius):
        self.tiles_matrix = [
            [0, 0, 1, 0, 1, 0, 1, 0, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0],
            [1, 0, 1, 0, 1, 0, 1, 0, 1],
            [0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 1, 0, 0],
        ]
        self.houses = set()
        self.roads = set()
        self.tiles = set()

        # RN03 e RN23: Ladrilhos e numerações do jogo base
        numbers = [2, 3, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
        types = [WHEAT, LAMB, TREE] * 4 + [ROCK, BRICK] * 3 + [DESERT]

        # --- PARÂMETROS DE CALIBRAGEM DA BORDA ---
        # Se a moldura parecer pequena/grande, ajuste estes multiplicadores:
        BORDER_SCALE_X = 11.5  # Aumentado para cobrir a largura total externa
        BORDER_SCALE_Y = 11.5  # Aumentado para cobrir a altura total externa

        # Se a moldura precisar de ser empurrada para alinhar com os recortes, ajuste aqui (em pixels):
        OFFSET_X = -4
        OFFSET_Y = -2

        l = cos(pi / 3) * hex_radius
        dx = l * sqrt(3 / 4) * 2
        dy = 3 * l

        center_x = x0 + (4 * dx)
        center_y = y0 + (2 * dy)

        loader = SpriteLoader()
        board_width = int(hex_radius * BORDER_SCALE_X)
        board_height = int(hex_radius * BORDER_SCALE_Y)
        self.border_sprite = loader.get_sprite("full_border", target_size=(board_width, board_height))

        self.border_rect = self.border_sprite.get_rect(
            center=(int(center_x + OFFSET_X), int(center_y + OFFSET_Y))
        )

        for i in range(len(self.tiles_matrix)):
            y = y0 + i * dy
            for j in range(len(self.tiles_matrix[i])):
                if self.tiles_matrix[i][j]:
                    x = x0 + j * dx
                    number = takesome(numbers)
                    type_ = takesome(types)
                    self.tiles_matrix[i][j] = HexagonTile(
                        number,
                        type_,
                        x,
                        y,
                        hex_radius,
                        j,
                        i,
                        self.tiles_matrix
                    )
                    self.tiles.add(self.tiles_matrix[i][j])
                else:
                    self.tiles_matrix[i][j] = None

        for row in self.tiles_matrix:
            for tile in row:
                if not tile:
                    continue
                tile.link()
                tile.create_houses()
                tile.create_roads()
                self.houses |= set(tile.extract_houses())
                self.roads |= set(tile.extract_roads())

        # RN12: Distribuição dos 9 portos de comércio
        self.port_hexagons = [
            self.tiles_matrix[0][2],
            self.tiles_matrix[0][4],
            self.tiles_matrix[1][1],
            self.tiles_matrix[1][7],
            self.tiles_matrix[2][8],
            self.tiles_matrix[3][1],
            self.tiles_matrix[3][7],
            self.tiles_matrix[4][2],
            self.tiles_matrix[4][4],
        ]

        self.port_positions = [
            'tl', 'tr', 'l', 'tr', 'r', 'l', 'br', 'bl', 'br'
        ]

        port_type = [BRICK, ROCK, TREE, LAMB, WHEAT] + [GENERIC] * 4

        self.ports = []
        for i, (port, pos) in enumerate(zip(self.port_hexagons, self.port_positions)):
            if pos == 'l':
                p1 = port.house_bottom_left
                p2 = port.house_top_left
            elif pos == 'tr':
                p1 = port.house_top
                p2 = port.house_top_right
            elif pos == 'tl':
                p1 = port.house_top_left
                p2 = port.house_top
            elif pos == 'r':
                p1 = port.house_top_right
                p2 = port.house_bottom_right
            elif pos == 'br':
                p1 = port.house_bottom_right
                p2 = port.house_bottom
            elif pos == 'bl':
                p1 = port.house_bottom
                p2 = port.house_bottom_left

            self.ports.append(Port(p1, p2, takesome(port_type)))

        self._link_entities()

    def _link_entities(self):
        houses_list = [h for h in self.houses if h]
        for h in houses_list:
            h.adjacent_houses = set()

        for r in self.roads:
            if not r:
                continue
            ha = next((h for h in houses_list if self._close(h.x, h.y, r.x0, r.y0)), None)
            hb = next((h for h in houses_list if self._close(h.x, h.y, r.x1, r.y1)), None)
            r.house_a, r.house_b = ha, hb
            if ha and hb:
                ha.adjacent_houses.add(hb)
                hb.adjacent_houses.add(ha)

    @staticmethod
    def _close(x1, y1, x2, y2, eps=2.0):
        return abs(x1 - x2) <= eps and abs(y1 - y2) <= eps

    def get_buildable_at(self, pos):
        for house in self.houses:
            if house and house.circle.collidepoint(pos):
                return house
        for road in self.roads:
            if road and road.collidepoint(pos):
                return road
        return None

    def get_adjacent_tiles(self, house):
        """Retorna os tiles adjacentes a uma casa."""
        adjacent = []
        for tile in self.tiles:
            houses = tile.extract_houses()
            if house in houses:
                adjacent.append(tile)
        return adjacent

    def distribute_initial_resources(self, player, house):
        """RN18: Distribui recursos dos tiles adjacentes à segunda aldeia."""
        from constants.types import DESERT
        adjacent_tiles = self.get_adjacent_tiles(house)
        for tile in adjacent_tiles:
            if tile.terrain_type != DESERT:
                player.inventory.add(tile.terrain_type, 1)

    def handle_event(self, event):
        for tile in self.tiles:
            tile.handle_event(event)

    def update(self, dt):
        for tile in self.tiles:
            tile.update(dt)
        for road in self.roads:
            road.update(dt)
        for house in self.houses:
            if house:
                house.update(dt)

    def render(self, surface):
        # 1. Camada de fundo: Renderiza a moldura oceânica
        if hasattr(self, 'border_sprite') and self.border_sprite:
            surface.blit(self.border_sprite, self.border_rect.topleft)

        # 2. Renderiza os terrenos e numerações
        for tile in self.tiles:
            tile.render(surface)

        # 3. Renderiza as docas portuárias
        for port in self.ports:
            port.render(surface)

        # 4. Renderiza as estradas
        for road in self.roads:
            road.render(surface)

        # 5. Renderiza as cidades e aldeias na camada superior
        for house in self.houses:
            if house:
                house.render(surface)