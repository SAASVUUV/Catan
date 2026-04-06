import pygame
import math

class Circle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color

    def render(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def collidecircle(self, other_circle):
        distance = ((self.x - other_circle.x)**2 + (self.y - other_circle.y)**2)**0.5
        return distance < (self.radius + other_circle.radius)
    
    def collidepoint(self, point):
        px, py = point
        distance = math.sqrt((px - self.x)**2 + (py - self.y)**2)
        return distance <= self.radius