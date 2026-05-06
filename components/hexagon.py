import math
import pygame
from .circle import Circle

class Hexagon:

    def __init__(self, radius, x, y, color):
        self.radius = radius
        self.x = x
        self.y = y
        self.color = color

        dr = 10
        self.circle = Circle(x, y, radius-dr, color)

        self.points = []
        for i in range(6):
            angle = -math.pi / 2 + i * (math.pi / 3)
            add_x = x + radius * math.cos(angle)
            add_y = y + radius * math.sin(angle)
            self.points.append((add_x, add_y))
        
        self.create_vertices()
        self.create_edges()
    
    def create_vertices(self):
        self.vertex_top = self.points[0]
        self.vertex_bottom = self.points[3]
        self.vertex_top_left = self.points[1]
        self.vertex_top_right = self.points[5]
        self.vertex_bottom_left = self.points[2]
        self.vertex_bottom_right = self.points[4]

    def create_edges(self):
        self.edge_left = (self.vertex_bottom_left, self.vertex_top_left)
        self.edge_right = (self.vertex_top_right, self.vertex_bottom_right)
        self.edge_top_left = (self.vertex_top_left, self.vertex_top)
        self.edge_top_right = (self.vertex_top, self.vertex_top_right)
        self.edge_bottom_left = (self.vertex_bottom, self.vertex_bottom_left)
        self.edge_bottom_right = (self.vertex_bottom_right, self.vertex_bottom)

    def update(self, dt):
        pass

    def handle_event(self, event):
        pass

    def collidepoint(self, point):
        return self.circle.collidepoint(point)

    def render(self, surface):
        pygame.draw.polygon(
            surface, 
            self.color, 
            self.points, 
            0
        )
