"""CardManager using the structured DevelopmentCard classes.

This manager keeps a minimal behavior: buying (deducting resources),
making newly bought cards ready at turn start, and activating cards
by delegating to the card objects.
"""
import random
import traceback

from constants.types import ROCK, LAMB, WHEAT
from components.base_card import (
    BaseCard,
    KnightCard,
    RoadBuildingCard,
    YearOfPlentyCard,
    MonopolyCard,
    VictoryPointCard,
)
from components.card_states import CardState


class CardManager:
    def __init__(self, players):
        self.players = players

    def _ensure_player_cards(self, player):
        if not hasattr(player, "development_cards"):
            player.development_cards = []
        if not hasattr(player, "played_development_card_this_turn"):
            player.played_development_card_this_turn = False

    def attempt_buy_card(self, player):
        """Attempt to buy a development card for `player`.

        Returns True on success, False on insufficient resources.
        """
        self._ensure_player_cards(player)
        # Cost: 1 ore (ROCK), 1 wool (LAMB), 1 wheat (WHEAT)
        if not (player.inventory.has(ROCK, 1) and player.inventory.has(LAMB, 1) and player.inventory.has(WHEAT, 1)):
            return False

        player.inventory.remove(ROCK, 1)
        player.inventory.remove(LAMB, 1)
        player.inventory.remove(WHEAT, 1)

        # Create a concrete development card randomly from available subclasses.
        # The purchased card is added in LOCKED/bought_this_turn state via
        # `Player.add_development_card` (keeps the rule that it cannot be
        # used the same turn it was bought).
        card_cls = random.choice([
            KnightCard,
            RoadBuildingCard,
            YearOfPlentyCard,
            MonopolyCard,
            VictoryPointCard,
        ])
        card = card_cls()
        player.add_development_card(card)
        return True

    def on_turn_start(self, player):
        """Called when a player's turn starts: make newly bought cards ready."""
        self._ensure_player_cards(player)
        for c in player.development_cards:
            if getattr(c, "bought_this_turn", False):
                c.bought_this_turn = False
                c.state = CardState.READY
        player.played_development_card_this_turn = False

    def attempt_activate_card(self, player, card, **kwargs):
        """Attempt to activate a card. Returns True on success.

        Additional context (e.g. `players`, `tabletop`, `edges`, `resources`)
        can be passed via kwargs and will be forwarded to the card's
        `activate` method.
        """
        self._ensure_player_cards(player)
        can, reason = card.can_activate(player.played_development_card_this_turn)
        if not can:
            return False

        try:
            # Provide basic context (players list and activating player) and
            # forward any extra kwargs the caller supplied.
            card.activate(turn_manager=self, players=self.players, player=player, **kwargs)
        except Exception as e:
            # Log detailed traceback to aid debugging in UI environment
            print(f"Error activating card {getattr(card, 'name', repr(card))} for player {getattr(player, 'name', None)}: {e}")
            traceback.print_exc()
            return False

        # Mark player as having played a development card this turn
        player.played_development_card_this_turn = True
        # Remove consumed/used cards from player's list so UI doesn't show them
        try:
            from components.card_states import CardState
            if getattr(card, 'state', None) == CardState.USED:
                if card in getattr(player, 'development_cards', []):
                    player.development_cards.remove(card)
        except Exception:
            # non-fatal: if anything goes wrong here, don't break game flow
            pass
        return True
