import pygame
from .base_scene import BaseScene
from core.player import Player
from core.turn_manager import TurnManager
from components.tabletop import Tabletop
from constants.colors import RED, BLUE, GREEN, BLACK, YELLOW

class Game(BaseScene):
    def __init__(self, manager=None):
        self.manager = manager
        self.players = [
            Player(1, "Player 1", RED),
            Player(2, "Player 2", BLUE),
            Player(3, "Player 3", GREEN),
            Player(4, "Player 4", YELLOW)
        ]
        self.turn_manager = TurnManager(self.players)        
        self.tabletop = Tabletop(100, 100, 50)
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def handle_event(self, event: pygame.event.Event):
        self.tabletop.handle_event(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        target = self.tabletop.get_buildable_at(pos)
        if target:
            # Tenta construir usando o jogador atual do TurnManager
            success = target.try_build(self.turn_manager.current_player)
            
            # Se a construção foi bem-sucedida, avançamos o turno automaticamente
            if success:
                self.turn_manager.next_turn()

    def update(self, dt: float):
        self.tabletop.update(dt)

    def render(self, surface: pygame.Surface):
        surface.fill(BLACK)
        self.tabletop.render(surface)