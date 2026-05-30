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

from components.card_states import CardState
from components.card_types import CardType


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
        if (card_type in [CardType.VICTORY_POINT, CardType.UNIVERSITY, CardType.MARKET, CardType.PALACE, CardType.CHAPEL, CardType.LIBRARY]):
            self.state: CardState = CardState.READY
        else:
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
        if self.state == CardState.USED:
            return False, "Carta já foi utilizada"
        if self.type in [CardType.VICTORY_POINT, CardType.UNIVERSITY, CardType.MARKET, CardType.PALACE, CardType.CHAPEL, CardType.LIBRARY]:
            return True, ""
        if self.state == CardState.LOCKED or self.bought_this_turn:
            return False, "Carta não está pronta (comprada neste turno)"
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
    card_type = CardType.KNIGHT
    def __init__(self, **kwargs):
        super().__init__(name="Knight", card_type=self.card_type, **kwargs)

    def activate(self, turn_manager=None, **kwargs):
        # Placeholder for robber-move effect
        return super().activate(turn_manager=turn_manager, **kwargs)


class ProgressCard(DevelopmentCard):
    card_type = CardType.PROGRESS
    def __init__(self, name: str, card_type: Optional[CardType] = None, **kwargs):
        # Passa o card_type recebido para a classe base, em vez de usar o seu próprio.
        super().__init__(name=name, card_type=card_type, **kwargs)

    def activate(self, turn_manager=None, **kwargs):
        # Placeholder for specific progress effect
        return super().activate(turn_manager=turn_manager, **kwargs)


class RoadBuildingCard(ProgressCard):
    card_type = CardType.ROAD_BUILDING
    def __init__(self, **kwargs):
        super().__init__(name="Construção de Estradas", card_type=self.card_type, **kwargs)

    def activate(self, turn_manager=None, players=None, tabletop=None, edges=None, **kwargs):
        """Place two roads on the board without consuming resources.

        Args expected in kwargs/context:
        - tabletop: the Tabletop instance containing `roads` set
        - edges: iterable of two Road objects (from tabletop.roads)
        - players: optional list of players (not required here)
        """
        super().activate(turn_manager=turn_manager, **kwargs)
        owner = self.owner
        if tabletop is None or edges is None or len(edges) == 0:
            raise ValueError("Road Building requires 'tabletop' and 'edges' (1-2) parameters")

        # Attempt to place up to two roads, but respect the player's existing
        # piece limit via `can_build_road()` so we reuse player logic.
        built = 0
        for edge in edges[:2]:
            # stop if player cannot build more roads
            if not owner.can_build_road():
                break
            success = edge.try_build(owner, tabletop.roads, force_free=True)
            if not success:
                # stop attempting further placements if one fails
                break
            built += 1

        return True

class YearOfPlentyCard(ProgressCard):
    card_type = CardType.YEAR_OF_PLENTY
    def __init__(self, **kwargs):
        super().__init__(name="Ano de Fartura", card_type=self.card_type, **kwargs)

    def activate(self, turn_manager=None, players=None, resources=None, bank=None, **kwargs):
        """Give the owner two resources chosen by the player.

        If a `bank` is provided, resources are taken from the bank and
        then given to the player. Otherwise resources are added directly
        to the player's inventory (backwards-compatible fallback).

        Expects `resources` to be an iterable of two resource identifiers.
        """
        super().activate(turn_manager=turn_manager, **kwargs)
        if resources is None or len(resources) != 2:
            raise ValueError("Year of Plenty requires 'resources' param with two resource types")

        for r in resources:
            if not hasattr(self.owner, 'inventory'):
                raise RuntimeError("Card owner has no inventory")

            if bank is not None:
                # Attempt to remove from bank; fail if not available
                ok = bank.remove(r, 1)
                if not ok:
                    raise RuntimeError("Banco sem recursos suficientes para Year of Plenty")
                self.owner.inventory.add(r, 1)
            else:
                # Backwards-compatible behavior
                self.owner.inventory.add(r, 1)

        return True

class MonopolyCard(ProgressCard):
    card_type = CardType.MONOPOLY
    def __init__(self, **kwargs):
        super().__init__(name="Monopólio", card_type=self.card_type, **kwargs)

    def activate(self, turn_manager=None, players=None, resource=None, **kwargs):
        """Take all of `resource` from other players and give to owner.

        Expects `players` to be an iterable of all players and `resource` the chosen type.
        """
        super().activate(turn_manager=turn_manager, **kwargs)
        if players is None:
            raise ValueError("Monopoly requires 'players' list")
        if resource is None:
            raise ValueError("Monopoly requires 'resource' param")

        for p in players:
            if p is self.owner:
                continue
            count = 0
            if hasattr(p, 'inventory'):
                count = p.inventory.get_count(resource)
            if count and count > 0:
                # remove from other player and add to owner
                p.inventory.remove(resource, count)
                self.owner.inventory.add(resource, count)

        return True

class VictoryPointCard(DevelopmentCard):
    def __init__(self, name: str, card_type: Optional[CardType] = None, **kwargs):
        # Passa o card_type recebido para a classe base, em vez de usar o seu próprio.
        super().__init__(name=name, card_type=card_type, **kwargs)

    def activate(self, turn_manager=None, player=None, **kwargs):
        """Activate the card, revealing it for victory points."""
        ok, reason = self.can_activate()
        if not ok:
            raise RuntimeError(f"Cannot activate card: {reason}")

        self.state = CardState.USED
        self.bought_this_turn = False
        #player.cards_points += 1
        # The actual VP increment is handled by game logic observing this state change
        return True

class UniversityCard(VictoryPointCard):
    card_type = CardType.UNIVERSITY
    def __init__(self, **kwargs):
        super().__init__(name="Universidade", card_type=self.card_type, **kwargs)


class MarketCard(VictoryPointCard):
    card_type = CardType.MARKET
    def __init__(self, **kwargs):
        super().__init__(name="Mercado", card_type=self.card_type, **kwargs)


class PalaceCard(VictoryPointCard):
    card_type = CardType.PALACE
    def __init__(self, **kwargs):
        super().__init__(name="Palácio", card_type=self.card_type, **kwargs)


class ChapelCard(VictoryPointCard):
    card_type = CardType.CHAPEL
    def __init__(self, **kwargs):
        super().__init__(name="Capela", card_type=self.card_type, **kwargs)


class LibraryCard(VictoryPointCard):
    card_type = CardType.LIBRARY
    def __init__(self, **kwargs):
        super().__init__(name="Biblioteca", card_type=self.card_type, **kwargs)
