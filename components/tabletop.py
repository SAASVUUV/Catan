from .hexagon_tile import HexagonTile
from .port import Port
from constants.types import *
from math import cos, pi, sqrt
from utils.myrandom import takesome

class Tabletop:

    def __init__(self, x0, y0, hex_radius):
        self.tiles_matrix = [
            [0,0,1,0,1,0,1,0,0],
            [0,1,0,1,0,1,0,1,0],
            [1,0,1,0,1,0,1,0,1],
            [0,1,0,1,0,1,0,1,0],
            [0,0,1,0,1,0,1,0,0],
        ]
        self.houses = set()
        self.roads = set()
        self.tiles = set()
        numbers = [2,3,3,3,4,4,5,5,6,6,8,8,9,9,10,10,11,11,12]
        types = [WHEAT, LAMB, TREE] * 4 + [ROCK, BRICK] * 3 + [DESERT]

        l = cos(pi/3)*hex_radius
        dx = l * sqrt(3/4)*2
        dy = 3*l
        for i in range(len(self.tiles_matrix)):
            y = y0+i*dy
            for j in range(len(self.tiles_matrix[i])):
                if(self.tiles_matrix[i][j]): 
                    x = x0+j*dx
                    number = takesome(numbers)
                    type = takesome(types)
                    self.tiles_matrix[i][j] = HexagonTile(
                        tile_number, # Passa None se for deserto
                        tile_type,
                        x, 
                        y,
                        hex_radius,
                        j,
                        i,
                        self.tiles_matrix
                    )
                    self.tiles.add(self.tiles_matrix[i][j])
                else: self.tiles_matrix[i][j] = None
        for row in self.tiles_matrix:
            for tile in row:
                if not tile:
                    continue
                tile.link()
                tile.create_houses()
                tile.create_roads()
                self.houses |= set(tile.extract_houses())
                self.roads |= set(tile.extract_roads())


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
        for i, (port, pos) in enumerate(zip(self.port_hexagons,self.port_positions)):
            if pos == 'l':
                p1 = port.house_bottom_left
                p2 = port.house_top_left
            if pos == 'tr':
                p1 = port.house_top
                p2 = port.house_top_right
            if pos == 'tl':
                p1 = port.house_top_left
                p2 = port.house_top
            if pos == 'r':
                p1 = port.house_top_right
                p2 = port.house_bottom_right
            if pos == 'br':
                p1 = port.house_bottom_right
                p2 = port.house_bottom
            if pos == 'bl':
                p1 = port.house_bottom
                p2 = port.house_bottom_left

            self.ports.append(Port(p1, p2, takesome(port_type)))


    def handle_event(self, event):
        for tile in self.tiles: tile.handle_event(event)
        for road in self.roads: road.handle_event(event)
        for house in self.houses: 
            if house: house.handle_event(event)

    def update(self, dt):
        for tile in self.tiles: tile.update(dt)
        for road in self.roads: road.update(dt)
        for house in self.houses: 
            if house: house.update(dt)

    def render(self, surface):
        for tile in self.tiles: tile.render(surface)
        for road in self.roads: road.render(surface)
        for house in self.houses: 
            if house: house.render(surface)