from components.base_card import (
    BaseCard,
    ChapelCard,
    LibraryCard,
    MarketCard,
    PalaceCard,
    UniversityCard,
    VictoryPointCard,
)
from components.card_states import CardState
from components.card_types import CardType
from constants.types import BRICK, LAMB, ROCK, TREE, WHEAT
from models.bank import Bank
from models.inventory import Inventory
from models.player import Player


def stock(player, **resources):
    mapping = {"rock": ROCK, "tree": TREE, "lamb": LAMB, "brick": BRICK, "wheat": WHEAT}
    for name, count in resources.items():
        player.inventory.add(mapping[name], count)


def test_inventory_add_remove_has_multiple_and_unknown_resources():
    inv = Inventory()
    inv.add(ROCK, 3)
    inv.add(999, 10)

    assert inv.get_count(ROCK) == 3
    assert inv.get_count(999) == 0
    assert inv.has_multiple({ROCK: 2, WHEAT: 0})
    assert not inv.remove(ROCK, 4)
    assert inv.remove(ROCK, 2)
    assert inv.total() == 1


def test_bank_tracks_counts_and_rejects_overdrafts():
    bank = Bank(initial_count=1)

    assert bank.has(BRICK)
    assert bank.remove(BRICK)
    assert not bank.has(BRICK)
    assert not bank.remove(BRICK)
    bank.add(BRICK, 2)
    bank.add(999, 5)
    assert bank.get_count(BRICK) == 2
    assert bank.get_count(999) == 5


def test_player_victory_points_visible_points_and_helpers():
    player = Player(1, "Alice", (1, 2, 3))
    player.settlements_count = 2
    player.cities_count = 1
    player.has_longest_road = True
    player.has_largest_army = True
    player.development_cards.extend([VictoryPointCard(), UniversityCard()])

    assert player.victory_points == 10
    assert player.visible_victory_points == 8
    assert player.played_knights_count == 0

    stock(player, rock=3, wheat=2, brick=4, tree=1, lamb=1)
    assert player.total_resources == 11
    assert player.get_most_abundant_resource() == BRICK
    assert player.get_least_abundant_resource() == TREE
    assert player.would_exceed_hand_limit()
    assert player.can_afford_anything()
    assert player.has_resources_for_dev_card()


def test_player_build_limits_setup_phase_and_successful_purchases():
    player = Player(1, "Builder", (10, 10, 10))
    assert player.is_in_setup_phase()
    assert player.can_build_settlement()
    assert player.can_build_city()
    assert player.can_build_road()

    stock(player, brick=2, tree=2, lamb=1, wheat=3, rock=3)
    assert player.buy_road()
    assert player.roads_count == 1
    assert player.buy_settlement()
    assert player.settlements_count == 1
    assert player.buy_city()
    assert player.settlements_count == 0
    assert player.cities_count == 1


def test_player_purchase_failures_cover_limits_and_missing_resources():
    player = Player(1, "Limited", (1, 1, 1))
    player.roads_count = 15
    player.settlements_count = 5
    player.cities_count = 4

    assert not player.buy_road()
    assert not player.buy_settlement()
    assert not player.buy_city()

    player.roads_count = player.settlements_count = player.cities_count = 0
    assert not player.buy_road()
    assert not player.buy_settlement()
    assert not player.buy_city()


def test_player_development_card_sets_owner_and_locked_state():
    player = Player(1, "Cards", (0, 0, 0))
    card = BaseCard("Cavaleiro", card_type=CardType.KNIGHT)

    player.add_development_card(card, purchase_turn=7)

    assert card.owner is player
    assert card.purchase_turn == 7
    assert card.bought_this_turn
    assert card.state == CardState.LOCKED


def test_player_abundance_helpers_return_none_for_empty_or_zero_inventory():
    player = Player(1, "Empty", (0, 0, 0))
    player.inventory.cards = {}
    assert player.get_most_abundant_resource() is None
    assert player.get_least_abundant_resource() is None

    player.inventory.cards = {ROCK: 0, TREE: 0}
    assert player.get_least_abundant_resource() is None


def test_victory_point_card_subclasses_are_reveal_only():
    for cls in [VictoryPointCard, UniversityCard, MarketCard, PalaceCard, ChapelCard, LibraryCard]:
        card = cls()
        can, reason = card.can_activate(has_played_card_this_turn=True)
        assert not can
        assert "ponto" in reason
        assert card.activate() is False
