"""Object model for Development Cards (architecture only).

Provides a `DevelopmentCard` base class and concrete subclasses for
Knight, Progress and Victory Point cards. Progress cards have specific
subclasses for Road Building, Year of Plenty and Monopoly.

This module only implements state transitions and activation scaffolding;
no gameplay effects are executed here.
"""
from __future__ import annotations

import uuid
from typing import Optional

from development_cards.card_states import CardState
from development_cards.card_types import CardType


class DevelopmentCard:
    def __init__(
        self,
        name: str,
        description: str = "",
        card_type: Optional[CardType] = None,
        owner=None,
        purchase_turn: Optional[int] = None,
        card_id: Optional[str] = None,
    ):
        self.id: str = card_id or str(uuid.uuid4())
        self.name: str = name
        self.description: str = description
        self.type: Optional[CardType] = card_type
        self.state: CardState = CardState.LOCKED
        self.owner = owner
        self.purchase_turn: Optional[int] = purchase_turn
        # Flag to indicate card was bought in the current turn
        self.bought_this_turn: bool = True

    def can_activate(self, has_played_card_this_turn: bool = False):
        """Return (bool, reason) whether the card can be activated now.

        Rules enforced here:
        - LOCKED / bought_this_turn cards cannot be activated.
        - USED cards cannot be activated.
        - Only one development card (except Victory Point) can be played per turn.
        """
        if self.state == CardState.LOCKED or self.bought_this_turn:
            return False, "Carta não está pronta (comprada neste turno)"
        if self.state == CardState.USED:
            return False, "Carta já foi utilizada"
        if has_played_card_this_turn and self.type != CardType.VICTORY_POINT:
            return False, "Já jogou uma carta de desenvolvimento neste turno"
        return True, ""

    def activate(self, turn_manager=None, **kwargs):
        """Activate the card.

        This base implementation performs only state transitions and basic
        validation. Subclasses should override to implement the actual effect
        (e.g., moving the robber, giving resources), but must call
        `super().activate(...)` or replicate the state updates.
        """
        ok, reason = self.can_activate(has_played_card_this_turn=bool(getattr(self.owner, "played_development_card_this_turn", False)))
        if not ok:
            raise RuntimeError(f"Cannot activate card: {reason}")

        # Mark as used; actual effects implemented in subclasses
        self.state = CardState.USED
        self.bought_this_turn = False
        return True

    def discard(self):
        """Discard the card (mark as used/discarded)."""
        self.state = CardState.USED
        self.bought_this_turn = False


# Backwards-compatible name used in tests
BaseCard = DevelopmentCard


class KnightCard(DevelopmentCard):
    def __init__(self, **kwargs):
        super().__init__(name="Knight", card_type=CardType.KNIGHT, **kwargs)

    def activate(self, turn_manager=None, **kwargs):
        # Placeholder for robber-move effect
        return super().activate(turn_manager=turn_manager, **kwargs)


class ProgressCard(DevelopmentCard):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, card_type=CardType.PROGRESS, **kwargs)

    def activate(self, turn_manager=None, **kwargs):
        # Placeholder for specific progress effect
        return super().activate(turn_manager=turn_manager, **kwargs)


class RoadBuildingCard(ProgressCard):
    def __init__(self, **kwargs):
        super().__init__(name="Road Building", **kwargs)


class YearOfPlentyCard(ProgressCard):
    def __init__(self, **kwargs):
        super().__init__(name="Year of Plenty", **kwargs)


class MonopolyCard(ProgressCard):
    def __init__(self, **kwargs):
        super().__init__(name="Monopoly", **kwargs)


class VictoryPointCard(DevelopmentCard):
    def __init__(self, **kwargs):
        super().__init__(name="Victory Point", card_type=CardType.VICTORY_POINT, **kwargs)

    def activate(self, turn_manager=None, **kwargs):
        # Revealing victory point should update player's visible score;
        # leave effect implementation for game logic; just move state.
        return super().activate(turn_manager=turn_manager, **kwargs)
