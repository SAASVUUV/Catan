from .hexagon_tile import HexagonTile
from constants.types import *
from math import cos, pi, sqrt
from random import randrange

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
                    number = numbers.pop(randrange(len(numbers)))
                    type = types.pop(randrange(len(types)))
                    self.tiles_matrix[i][j] = HexagonTile(
                        number,
                        type,
                        x, 
                        y,
                        hex_radius,
                        j,
                        i,
                        self.tiles_matrix
                    )
                    self.houses = self.houses | set(self.tiles_matrix[i][j].extract_houses())
                    self.roads = self.roads | set(self.tiles_matrix[i][j].extract_roads())
                    self.tiles.add(self.tiles_matrix[i][j])
                else: self.tiles_matrix[i][j] = None

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        for tile in self.tiles: tile.render(surface)
        for road in self.roads: road.render(surface)
        for house in self.houses: 
            if house: house.render(surface)