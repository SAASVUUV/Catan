from constants.types import *

class Player:
    def __init__(self, name):
        self.name = name
        self.resources = {WHEAT: 0, LAMB: 0, TREE: 0, ROCK: 0, BRICK: 0}
        self.houses_count = 0