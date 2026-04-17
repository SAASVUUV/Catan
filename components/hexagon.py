import math
import pygame
from .circle import Circle

class Hexagon:

    def __init__(self, radius, x, y, color):
        self.radius = radius
        self.x = x
        self.y = y
        self.color = color

        self.circle = Circle(x, y, radius, color)

        self.points = []
        for i in range(3, 10): # Começa com 90º
            angle = i * (math.pi / 3) 
            add_x = x + radius * math.cos(angle)
            add_y = y + radius * math.sin(angle)
            self.points.append((add_x, add_y))
        
        self.top_middle = self.points[0]
        self.top_left = self.points[1]
        self.bottom_left = self.points[2]
        self.bottom_middle = self.points[3]
        self.bottom_right = self.points[4]
        self.top_right = self.points[5]

    def update(self):
        pass

    def handle_event(self):
        pass

    def collidepoint(self, point):
        px, py = point
        return self.circle.collidepoint(px, py)

    def render(self, surface):
        pygame.draw.polygon(
            surface, 
            self.color, 
            self.points, 
            0
        )
    




    


# Loop principal
rodando = True
while rodando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
    
    tela.fill((255, 255, 255))
    desenhar_hexagono(tela, AZUL, (200, 200), 50)
    pygame.display.flip()

pygame.quit()