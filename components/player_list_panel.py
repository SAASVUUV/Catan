import pygame
from constants.colors import BEIGE_LIGHT, BROWN_DARK, BLACK, WHITE


class PlayerListPanel:
    def __init__(self, x, y, width, players, scale: float = 1.0):
        self.x = x
        self.y = y
        self.width = width
        self.players = players
        self.current_player = None
        self.row_height = int(45 * scale)
        self.height = len(players) * self.row_height + int(15 * scale)
        self.circle_radius = int(12 * scale)
        self.padding = int(8 * scale)

        font_size = int(24 * scale)
        font_bold_size = int(26 * scale)
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, font_size)
        self.font_bold = pygame.font.Font(caminho_fonte, font_bold_size)

    def set_current_player(self, player):
        self.current_player = player

    def render(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, BEIGE_LIGHT, rect, border_radius=8)
        pygame.draw.rect(surface, BROWN_DARK, rect, width=2, border_radius=8)

        circle_x = self.x + self.padding + self.circle_radius
        text_x = self.x + self.padding * 2 + self.circle_radius * 2 + 5

        for i, player in enumerate(self.players):
            row_y = self.y + self.padding + i * self.row_height
            row_center_y = row_y + self.row_height // 2
            is_current = player == self.current_player

            pygame.draw.circle(surface, player.color, (circle_x, row_center_y), self.circle_radius)

            if is_current:
                highlight_rect = pygame.Rect(text_x - 5, row_y, self.width - text_x + self.x - 5, self.row_height - 2)
                pygame.draw.rect(surface, (200, 195, 170), highlight_rect, border_radius=4)
                name_text = self.font_bold.render(player.name, True, BLACK)
            else:
                name_text = self.font.render(player.name, True, BROWN_DARK)

            text_y = row_center_y - name_text.get_height() // 2
            surface.blit(name_text, (text_x, text_y))

            score_text = self.font.render(str(player.victory_points), True, BLACK)
            surface.blit(score_text, (self.x + self.width - score_text.get_width() - self.padding, text_y))
