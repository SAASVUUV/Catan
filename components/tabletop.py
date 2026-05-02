from .hexagon_tile import HexagonTile
from constants.types import *
from math import cos, pi
from random import choice

class Tabletop:

    def __init__(self, x0, y0, hex_radius):
        self.tiles = [
            [0,0,1,0,1,0,1,0,0],
            [0,1,0,1,0,1,0,1,0],
            [1,0,1,0,1,0,1,0,1],
            [0,1,0,1,0,1,0,1,0],
            [0,0,1,0,1,0,1,0,0],
        ]
        self.houses = dict()
        self.roads = dict()
        numbers = [2,3,3,3,4,5,5,6,6,8,8,9,9,10,10,11,11,12]
        type = [WHEAT, LAMB, TREE] * 4 + [ROCK, BRICK] * 3 + [DESERT]

        dx = cos(pi/3)*hex_radius/2
        dy = hex_radius*1.5
        for i in range(len(self.tiles)):
            y = y0+i*dy
            for j in range(len(self.tiles[i])):
                if(self.tiles[i][j]): 
                    x = x0+j*dx
                    self.tiles[i][j] = HexagonTile(
                        choice(numbers),
                        choice(type),
                        x, 
                        y,
                        j,
                        i,
                        self.tiles
                    )
                    self.houses.add(self.tiles[i][j].extract_houses())
                    self.roads.add(self.tiles[i][j].extract_roads())
                else: self.tiles[i][j] = None

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        pass
