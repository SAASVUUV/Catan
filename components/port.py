import pygame
from utils.mymath import take_third_point
from constants.types import GENERIC
from constants.colors import BROWN_WOOD
from components.circle import Circle

class Port:

    def __init__(self, house1, house2, type):
        self.house1 = house1
        self.house2 = house2

        x1, y1 = self.house1.x, self.house1.y
        x2, y2 = self.house2.x, self.house2.y

        self.x, self.y = take_third_point(x1, y1, x2, y2)

        self.type = type
        self.ratio = 3 if type == GENERIC else 2
        
        self.ship = Circle(self.x, self.y, 10, BROWN_WOOD)

    
    def render(self, surface):
        pygame.draw.line(surface, BROWN_WOOD, (self.x, self.y), (self.house1.x, self.house1.y), 5)
        pygame.draw.line(surface, BROWN_WOOD, (self.x, self.y), (self.house2.x, self.house2.y), 5)
        self.ship.render(surface)