import math
import pygame
from .circle import Circle
from utils.sprites import SpriteLoader


class Hexagon:

    def __init__(self, radius, x, y, color, terrain_type=None):
        self.radius = radius
        self.x = x
        self.y = y
        self.color = color
        self.terrain_type = terrain_type

        dr = 10
        self.circle = Circle(x, y, radius - dr, color)

        self.points = []
        for i in range(6):
            angle = -math.pi / 2 + i * (math.pi / 3)
            add_x = x + radius * math.cos(angle)
            add_y = y + radius * math.sin(angle)
            self.points.append((add_x, add_y))

        self.create_vertices()
        self.create_edges()

        self.sprite = None
        if self.terrain_type is not None:
            w = int(radius * math.sqrt(3))
            h = int(radius * 2)
            self.sprite = SpriteLoader().get_terrain_sprite(self.terrain_type, target_size=(w, h))
            self.sprite_rect = self.sprite.get_rect(center=(int(x), int(y)))

    def create_vertices(self):
        self.vertex_top = self.points[0]
        self.vertex_bottom = self.points[3]
        self.vertex_top_left = self.points[5]
        self.vertex_top_right = self.points[1]
        self.vertex_bottom_left = self.points[4]
        self.vertex_bottom_right = self.points[2]

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
        if self.sprite:
            surface.blit(self.sprite, self.sprite_rect.topleft)
        else:
            pygame.draw.polygon(surface, self.color, self.points, 0)
            pygame.draw.polygon(surface, (50, 50, 50), self.points, 2)