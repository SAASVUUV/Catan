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
                    
                    # 1. Sorteia o tipo primeiro
                    tile_type = types.pop(randrange(len(types)))
                    
                    # 2. Só sorteia o número se NÃO for deserto
                    tile_number = None
                    if tile_type != DESERT:
                        tile_number = numbers.pop(randrange(len(numbers)))
                    
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

    def distribute_initial_resources(self, player, house_instance):
        print(f"--- Debug: Distribuindo para {player.name} ---")
        found_at_least_one = False
        
        for tile in self.tiles:
            if house_instance in tile.extract_houses():
                found_at_least_one = True
                print(f"Casa encosta no Tile: Tipo={tile.terrain_type}, Numero={tile.number}")
                
                if tile.terrain_type != DESERT and tile.number is not None:
                    player.resources[tile.terrain_type] += 1
        
        if not found_at_least_one:
            print("AVISO: Esta instância de casa não foi encontrada em nenhum tile!")
            
        print(f"Recursos finais: {player.resources}")
