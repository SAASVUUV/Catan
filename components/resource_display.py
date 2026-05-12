import pygame
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT
from constants.colors import BEIGE_MEDIUM, BROWN_DARK
from constants.types_colors import RESOURCE_COLORS
from models.inventory import TRADEABLE_RESOURCES

RESOURCE_NAMES = {
    ROCK: "Pedra",
    TREE: "Madeira",
    LAMB: "La",
    BRICK: "Tijolo",
    WHEAT: "Trigo"
}

class ResourceDisplay:
    CARD_WIDTH = 40
    CARD_HEIGHT = 55
    CARD_SPACING = 8

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.player = None
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, 16)

    def set_player(self, player):
        self.player = player

    def handle_event(self, event) -> bool:
        return False

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        if not self.player:
            return

        bg_rect = pygame.Rect(
            self.x - 10,
            self.y - 10,
            len(TRADEABLE_RESOURCES) * (self.CARD_WIDTH + self.CARD_SPACING) + 10,
            self.CARD_HEIGHT + 20
        )
        pygame.draw.rect(surface, BEIGE_MEDIUM, bg_rect, border_radius=6)
        pygame.draw.rect(surface, BROWN_DARK, bg_rect, width=2, border_radius=6)

        for i, resource in enumerate(TRADEABLE_RESOURCES):
            card_x = self.x + i * (self.CARD_WIDTH + self.CARD_SPACING)
            card_y = self.y

            color = RESOURCE_COLORS.get(resource, (200, 200, 200))
            card_rect = pygame.Rect(card_x, card_y, self.CARD_WIDTH, self.CARD_HEIGHT)
            pygame.draw.rect(surface, color, card_rect, border_radius=4)
            pygame.draw.rect(surface, BROWN_DARK, card_rect, width=2, border_radius=4)

            count = self.player.inventory.get_count(resource)
            count_text = self.font.render(str(count), True, BROWN_DARK)
            count_rect = count_text.get_rect(center=card_rect.center)
            surface.blit(count_text, count_rect)
