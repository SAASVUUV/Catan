import pygame
from constants.colors import BEIGE_LIGHT, BROWN_DARK, BLACK, WHITE


class PlayerListPanel:
    def __init__(self, x, y, width, players):
        self.x = x
        self.y = y
        self.width = width
        self.players = players
        self.current_player = None
        self.row_height = 28
        self.height = len(players) * self.row_height + 10

        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, 16)
        self.font_bold = pygame.font.Font(caminho_fonte, 18)

    def set_current_player(self, player):
        self.current_player = player

    def render(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, BEIGE_LIGHT, rect, border_radius=8)
        pygame.draw.rect(surface, BROWN_DARK, rect, width=2, border_radius=8)

        for i, player in enumerate(self.players):
            row_y = self.y + 5 + i * self.row_height
            is_current = player == self.current_player

            pygame.draw.circle(surface, player.color, (self.x + 15, row_y + 12), 8)

            if is_current:
                highlight_rect = pygame.Rect(self.x + 25, row_y, self.width - 35, self.row_height - 2)
                pygame.draw.rect(surface, (200, 195, 170), highlight_rect, border_radius=4)
                name_text = self.font_bold.render(player.name, True, BLACK)
            else:
                name_text = self.font.render(player.name, True, BROWN_DARK)

            surface.blit(name_text, (self.x + 30, row_y + 4))

            score_text = self.font.render(str(player.victory_points), True, BLACK)
            surface.blit(score_text, (self.x + self.width - 25, row_y + 4))
