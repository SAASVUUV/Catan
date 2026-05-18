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
    def __init__(self, x: int, y: int, scale: float = 1.0):
        self.x = x
        self.y = y
        self.player = None
        self.card_width = int(44 * scale)
        self.card_height = int(66 * scale)
        self.card_spacing = int(9 * scale)
        font_size = int(24 * scale)
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, font_size)

    def set_player(self, player):
        self.player = player

    def handle_event(self, event) -> bool:
        return False

    def update(self, dt: float):
        pass

    def render(self, surface: pygame.Surface):
        if not self.player:
            return

        padding = 15
        bg_rect = pygame.Rect(
            self.x - padding,
            self.y - padding,
            len(TRADEABLE_RESOURCES) * (self.card_width + self.card_spacing) + padding,
            self.card_height + padding * 2
        )
        pygame.draw.rect(surface, BEIGE_MEDIUM, bg_rect, border_radius=8)
        pygame.draw.rect(surface, BROWN_DARK, bg_rect, width=2, border_radius=8)

        for i, resource in enumerate(TRADEABLE_RESOURCES):
            card_x = self.x + i * (self.card_width + self.card_spacing)
            card_y = self.y

            color = RESOURCE_COLORS.get(resource, (200, 200, 200))
            card_rect = pygame.Rect(card_x, card_y, self.card_width, self.card_height)
            pygame.draw.rect(surface, color, card_rect, border_radius=6)
            pygame.draw.rect(surface, BROWN_DARK, card_rect, width=2, border_radius=6)

            count = self.player.inventory.get_count(resource)
            count_text = self.font.render(str(count), True, BROWN_DARK)
            count_rect = count_text.get_rect(center=card_rect.center)
            surface.blit(count_text, count_rect)
