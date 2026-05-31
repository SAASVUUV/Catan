import pygame
from constants.types import ROCK, TREE, LAMB, BRICK, WHEAT
from models.inventory import Inventory
from components.card_states import CardState


class Player:
    def __init__(self, player_id: int, name: str, color: tuple, is_bot: bool = False):
        self.id = player_id
        self.name = name
        self.color = color
        self.is_bot = is_bot

        # Contagem de estruturas ativas no tabuleiro
        self.settlements_count = 0
        self.cities_count = 0
        self.roads_count = 0

        # Cartas de desenvolvimento
        self.development_cards = []

        # Inventário de matérias-primas
        self.inventory = Inventory()
        # Flag to prevent playing more than one development card per turn
        self.played_development_card_this_turn = False

        # Conquistas especiais
        self.has_longest_road = False
        self.has_largest_army = False
        self.knights_played = 0
        
        # Tracking for bot actions
        self.turns_since_last_dev_card = 0

    @property
    def played_knights_count(self):
        """Retorna o número de cartas de cavaleiro jogadas."""
        return self.knights_played

    @property
    def victory_points(self):
        """RN6, RN8: Calcula o total de pontos de vitória do jogador (incluindo cartas VP e bônus)."""
        from components.base_card import VictoryPointCard
        vp_from_cards = sum(1 for c in self.development_cards if isinstance(c, VictoryPointCard))
        bonus = 0
        if self.has_longest_road:
            bonus += 2
        if self.has_largest_army:
            bonus += 2
        return self.settlements_count + (self.cities_count * 2) + vp_from_cards + bonus

    @property
    def visible_victory_points(self):
        """Pontos de vitória visíveis (construções + bônus de conquistas)."""
        bonus = 0
        if self.has_longest_road:
            bonus += 2
        if self.has_largest_army:
            bonus += 2
        return self.settlements_count + (self.cities_count * 2) + bonus

    # --- VERIFICAÇÃO DE FASE DO JOGO ---
    def is_in_setup_phase(self) -> bool:
        """
        RN17: Retorna True se o jogador ainda estiver posicionando
        as suas 2 aldeias e 2 estradas iniciais gratuitas.
        """
        return self.settlements_count < 2 or self.roads_count < 2

    # --- VALIDAÇÃO DE LIMITES DE PEÇAS (RF09) ---
    def can_build_settlement(self, max_limit: int = 5) -> bool:
        return self.settlements_count < max_limit

    def can_build_city(self, max_limit: int = 4) -> bool:
        return self.cities_count < max_limit

    def can_build_road(self, max_limit: int = 15) -> bool:
        return self.roads_count < max_limit

    # --- VALIDAÇÃO DE CUSTOS DE MATÉRIA-PRIMA (RN24) ---
    def has_resources_for_road(self) -> bool:
        return self.inventory.has(BRICK, 1) and self.inventory.has(TREE, 1)

    def has_resources_for_settlement(self) -> bool:
        return (self.inventory.has(BRICK, 1) and
                self.inventory.has(TREE, 1) and
                self.inventory.has(LAMB, 1) and
                self.inventory.has(WHEAT, 1))

    def has_resources_for_city(self) -> bool:
        return self.inventory.has(ROCK, 3) and self.inventory.has(WHEAT, 2)

    # --- AÇÕES PURAS DE ESTADO (Usadas no Setup) ---
    def add_road(self):
        self.roads_count += 1

    def add_settlement(self):
        self.settlements_count += 1

    def upgrade_to_city(self):
        self.settlements_count -= 1
        self.cities_count += 1 

    # --- AÇÕES FINANCEIRAS / COMPRA (Fase Principal - RF21) ---
    def buy_road(self, max_limit: int = 15) -> bool:
        if self.can_build_road(max_limit) and self.has_resources_for_road():
            self.inventory.remove(BRICK, 1)
            self.inventory.remove(TREE, 1)
            self.add_road()
            return True
        return False

    def buy_settlement(self, max_limit: int = 5) -> bool:
        if self.can_build_settlement(max_limit) and self.has_resources_for_settlement():
            self.inventory.remove(BRICK, 1)
            self.inventory.remove(TREE, 1)
            self.inventory.remove(LAMB, 1)
            self.inventory.remove(WHEAT, 1)
            self.add_settlement()
            return True
        return False

    def buy_city(self, max_limit: int = 4) -> bool:
        if self.settlements_count > 0 and self.can_build_city(max_limit) and self.has_resources_for_city():
            self.inventory.remove(ROCK, 3)
            self.inventory.remove(WHEAT, 2)
            self.upgrade_to_city()
            return True
        return False

    # --- Development cards management ---
    def add_development_card(self, card, purchase_turn: int = None):
        """Attach a development card to this player.

        Sets ownership and marks the card as bought this turn (LOCKED).
        """
        card.owner = self
        card.purchase_turn = purchase_turn
        card.bought_this_turn = True
        card.state = CardState.LOCKED
        self.development_cards.append(card)

    # --- Bot Helper Methods ---
    @property
    def total_resources(self) -> int:
        """Count total resources in hand."""
        return self.inventory.total()

    def get_resource_counts(self) -> dict:
        """Return copy of current resources."""
        return dict(self.inventory.cards)

    def get_most_abundant_resource(self) -> int:
        """Return the resource type with most cards, or None."""
        counts = self.get_resource_counts()
        if not counts:
            return None
        return max(counts.items(), key=lambda x: x[1])[0]

    def get_least_abundant_resource(self) -> int:
        """Return the resource type with least cards (excluding 0), or None."""
        counts = self.get_resource_counts()
        if not counts:
            return None
        non_zero = {k: v for k, v in counts.items() if v > 0}
        if not non_zero:
            return None
        return min(non_zero.items(), key=lambda x: x[1])[0]

    def would_exceed_hand_limit(self, additional: int = 0) -> bool:
        """Check if player would have >7 cards total."""
        return self.inventory.total() + additional > 7

    def can_afford_anything(self) -> bool:
        """Check if player can afford any construction."""
        return (self.has_resources_for_road() or 
                self.has_resources_for_settlement() or 
                self.has_resources_for_city())

    def has_resources_for_dev_card(self) -> bool:
        """Check if player can buy a development card."""
        return self.inventory.has(ROCK, 1) and self.inventory.has(LAMB, 1) and self.inventory.has(WHEAT, 1)
