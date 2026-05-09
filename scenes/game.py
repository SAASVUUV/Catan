from core.player import Player
from .base_scene import BaseScene
from components.tabletop import Tabletop
import pygame
from constants.colors import BLACK
from core.player import Player

class Game(BaseScene):
    def __init__(self, manager=None):
        super().__init__(manager)        
        self.tabletop = Tabletop(100, 100, 50)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.current_player = Player("Guilherme")
        
        # Simulando a colocação de duas casas
        all_houses = list(self.tabletop.houses)
        if len(all_houses) >= 2:
            # 1. Coloca a primeira casa (não ganha nada)
            self.build_house(self.current_player, all_houses[0])
            
            # 2. Coloca a segunda casa (deve disparar a distribuição)
            self.build_house(self.current_player, all_houses[1])

    def handle_event(self, event: pygame.event.Event):
        self.tabletop.handle_event(event)

    def update(self, dt: float):
        self.tabletop.update(dt)

    def render(self, surface: pygame.Surface):
        surface.fill(BLACK)
        self.tabletop.render(surface)

    def build_house(self, player, house):
        house.owner = player
        player.houses_count += 1
        
<<<<<<< Updated upstream
        # Lógica da Tarefa 4: só distribui na segunda construção
=======
>>>>>>> Stashed changes
        if player.houses_count == 2:
            self.tabletop.distribute_initial_resources(player, house)
