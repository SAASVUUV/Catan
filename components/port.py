import constants.types as types
from enum import Enum, auto

port_types = {
    "GENERIC": ["generic", 0],
    "TREE": ["tree", 1],
    "LAMB": ["lamb", 2],
    "WHEAT": ["wheat", 3],
    "BRICK": ["brick", 4],
    "ROCK": ["rock", 5],
}

class Port:
    def __init__(self, port_type = port_types["GENERIC"]):
        self.port_type = port_type
        if self.port_type[1] == 0:
            self.trade_ratio = 3
        else:
            self.trade_ratio = 2

    def get_trade_ratio(self):
        return self.trade_ratio

    def get_resource_type(self):
        return self.port_type[0]
    
    def get_resource_id(self):
        return self.port_type[1]

