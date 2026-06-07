import pygame
from typing import List, Tuple
from typing import List, Tuple, Optional
from utils.resources import resource_path

from components.card_states import CardState
from components.card_types import CardType
from components.base_card import DevelopmentCard
from constants.colors import BEIGE_MEDIUM, BROWN_DARK, GOLD


class DevelopmentDisplay:
    """HUD display that shows aggregated development card types for a player.

    Reuses sizing and layout similar to `ResourceDisplay` to keep consistent UI.
    """
    def __init__(self, x: int, y: int, scale: float = 1.0):
        self.x = int(x)
        self.y = int(y)
        self.xy = (self.x, self.y)
        self.card_width = int(44 * scale)
        self.card_height = int(66 * scale)
        self.card_spacing = int(9 * scale)
        caminho_fonte = resource_path('assets', 'fonts', 'MedievalSharp-Regular.ttf')
        try:
            self.font = pygame.font.Font(caminho_fonte, int(18 * scale))
            self.title_font = pygame.font.Font(caminho_fonte, int(14 * scale))
        except Exception:
            self.font = pygame.font.SysFont("Arial", int(18 * scale))
            self.title_font = pygame.font.SysFont("Arial", int(14 * scale))

        self.player = None
        self.hover_index = None

        # Color mapping per card type/subtype (parent-based with small variations)
        self.color_map = {
            str(CardType.KNIGHT): (100, 140, 220),
            str(CardType.PROGRESS): (120, 180, 120),
            str(CardType.UNIVERSITY): (218, 165, 32),
            str(CardType.MARKET): (220, 200, 120),
            str(CardType.PALACE): (160, 120, 80),
            str(CardType.CHAPEL): (140, 60, 180),
            str(CardType.LIBRARY): (160, 120, 80),
            # progress subtypes by class name
            "RoadBuildingCard": (160, 120, 80),
            "YearOfPlentyCard": (220, 200, 120),
            "MonopolyCard": (140, 60, 180),
        }

    def set_player(self, player):
        self.player = player

    def handle_event(self, event):
        """Handles user input.

        Returns:
        - a `DevelopmentCard` instance when a playable card was clicked
        - a tuple `(None, message)` when the user clicked a blocked/locked group
        - `None` when the event was not handled by this widget
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            groups = self._groups()
            for i, (_k, _count, cards) in enumerate(groups):
                card_x = self.x + i * (self.card_width + self.card_spacing)
                card_y = self.y
                rect = pygame.Rect(card_x, card_y, self.card_width, self.card_height)
                if rect.collidepoint(pos):
                    # Clicked on a card group. Find the first playable card.
                    for card in cards:
                        if card.state == CardState.READY or card.type in [CardType.VICTORY_POINT, CardType.UNIVERSITY, CardType.MARKET, CardType.PALACE, CardType.CHAPEL, CardType.LIBRARY]:
                            return card  # Return the card to be activated

                    # No READY card: attempt to show a helpful reason to the user.
                    if self.player and cards:
                        for card in cards:
                            try:
                                can, reason = card.can_activate(getattr(self.player, 'played_development_card_this_turn', False))
                                if not can and reason:
                                    return (None, reason)
                            except Exception:
                                continue
                    # Generic message
                    return (None, "Nenhuma carta disponível para jogar")
        return None

    def update(self, dt: float = 0.0):
        self.hover_index = None
        pos = pygame.mouse.get_pos()
        groups = self._groups()
        for i, (_k, _count, _cards) in enumerate(groups):
            card_x = self.x + i * (self.card_width + self.card_spacing)
            card_y = self.y
            rect = pygame.Rect(card_x, card_y, self.card_width, self.card_height)
            if rect.collidepoint(pos):
                self.hover_index = i
                break

    def _groups(self) -> List[Tuple[str, int, List[object]]]:
        """Aggregate player's cards by (type/subtype) and return list of (key, count, cards).

        Key is a display string identifying the group (uses card.name in Portuguese).
        """
        if not self.player:
            return []
        groups = {}
        for c in getattr(self.player, "development_cards", []):
            if c is None:
                continue
            # Use card.name for display (Portuguese names)
            key = getattr(c, "name", c.__class__.__name__)
            groups.setdefault(key, []).append(c)

        items = [(k, len(v), v) for k, v in groups.items()]
        # sort by count desc to show most relevant up to 5
        items.sort(key=lambda x: x[1], reverse=True)
        if len(items) > 5:
            self.x = self.xy[0] - (self.card_width + self.card_spacing) * (len(items) - 5)
        else:
            self.x = self.xy[0]
        return items


    def render(self, surface: pygame.Surface):
        if not self.player:
            return

        groups = self._groups()
        if not groups:
            # Draw empty background similar to resource display
            padding = 15
            bg_rect = pygame.Rect(
                self.x - padding,
                self.y - padding,
                max(len(groups), 5) * (self.card_width + self.card_spacing) + padding,
                self.card_height + padding * 2,
            )
            pygame.draw.rect(surface, BEIGE_MEDIUM, bg_rect, border_radius=8)
            pygame.draw.rect(surface, BROWN_DARK, bg_rect, width=2, border_radius=8)
            # Two-line centered message to avoid overflow
            line1 = "Nenhuma carta de"
            line2 = "desenvolvimento"
            f1 = self.title_font
            f2 = self.font
            s1 = f1.render(line1, True, BROWN_DARK)
            s2 = f2.render(line2, True, BROWN_DARK)
            total_h = s1.get_height() + s2.get_height() + 6
            start_y = bg_rect.top + (bg_rect.height - total_h) // 2
            surface.blit(s1, (bg_rect.centerx - s1.get_width() // 2, start_y))
            surface.blit(s2, (bg_rect.centerx - s2.get_width() // 2, start_y + s1.get_height() + 6))
            return

        # draw background area sized for up to 5 cards
        padding = 15
        bg_rect = pygame.Rect(
            self.x - padding,
            self.y - padding,
            max(len(groups), 5) * (self.card_width + self.card_spacing) + padding,
            self.card_height + padding * 2,
        )
        pygame.draw.rect(surface, BEIGE_MEDIUM, bg_rect, border_radius=8)
        pygame.draw.rect(surface, BROWN_DARK, bg_rect, width=2, border_radius=8)

        for i, (key, count, cards) in enumerate(groups):
            card_x = self.x + i * (self.card_width + self.card_spacing)
            card_y = self.y
            rect = pygame.Rect(card_x, card_y, self.card_width, self.card_height)

            # determine color
            color = self.color_map.get(key, self.color_map.get(str(cards[0].type), (180, 180, 180)))
            pygame.draw.rect(surface, color, rect, border_radius=6)
            pygame.draw.rect(surface, BROWN_DARK, rect, width=2, border_radius=6)

            # Count large in center
            count_text = self.title_font.render(str(count), True, BROWN_DARK)
            surface.blit(count_text, count_text.get_rect(center=rect.center))

            # Top-right placeholder for icon (empty box)
            icon_rect = pygame.Rect(rect.right - 16, rect.top + 6, 10, 10)
            pygame.draw.rect(surface, (220, 220, 220), icon_rect)
            pygame.draw.rect(surface, BROWN_DARK, icon_rect, width=1)

            # No state overlays: HUD shows aggregated counts only

            # Hover highlight
            if self.hover_index == i:
                pygame.draw.rect(surface, GOLD, rect, width=2, border_radius=6)
                # Tooltip: show key and count only
                tooltip = f"{key} ({count})"
                tip = self.font.render(tooltip, True, (255, 255, 255))
                tip_bg = pygame.Surface((tip.get_width() + 8, tip.get_height() + 6), flags=pygame.SRCALPHA)
                tip_bg.fill((40, 40, 40, 220))
                tx = rect.x
                ty = rect.y - tip_bg.get_height() - 6
                if ty < 0:
                    ty = rect.y + rect.h + 6
                surface.blit(tip_bg, (tx, ty))
                surface.blit(tip, (tx + 4, ty + 3))
