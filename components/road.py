import pygame
from .buildable import Buildable

MAX_ROADS = 15

class Road(Buildable):

    def __init__(self, edge):
        self.owner = None           
        super().__init__()         

        x0, y0 = edge[0]
        x1, y1 = edge[1]
        self.x0, self.y0 = x0, y0
        self.x1, self.y1 = x1, y1
        self._invalid_timer = 0.0
        self.house_a = None 
        self.house_b = None 


    def _can_place_road(self, player):
        if self.owner is not None:
            return False
        if not player.can_build_road(MAX_ROADS):
            return False
        
        #TODO adicionar a verificação de adjacência
        
        return True


    def try_build(self, player) -> bool:
        if not self._can_place_road(player):
            self._invalid_timer = 0.4
            return False
        
        self.owner = player
        self.color = player.color  
        player.add_road()
        return True


    def update(self, dt):
        if self._invalid_timer > 0:
            self._invalid_timer = max(0.0, self._invalid_timer - dt)

    def render(self, surface):
        color = self.owner.color if self.owner else getattr(self, 'color', (180, 180, 180))
        width = 4 if self.owner else 2
        
        pygame.draw.line(surface, color, (int(self.x0), int(self.y0)), (int(self.x1), int(self.y1)), width)
        
        if self._invalid_timer > 0:
            pygame.draw.line(surface, (200, 40, 40), (int(self.x0), int(self.y0)), (int(self.x1), int(self.y1)), width + 2)


    def collidepoint(self, pos, tolerance=5):
        px, py = pos
        dx, dy = self.x1 - self.x0, self.y1 - self.y0
        length_sq = dx*dx + dy*dy
        if length_sq == 0:
            return False
        t = max(0, min(1, ((px - self.x0)*dx + (py - self.y0)*dy) / length_sq))
        nearest_x = self.x0 + t*dx
        nearest_y = self.y0 + t*dy
        return (px - nearest_x)**2 + (py - nearest_y)**2 <= tolerance**2