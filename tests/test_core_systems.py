from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from components.base_card import BaseCard, KnightCard, RoadBuildingCard, YearOfPlentyCard
from components.card_states import CardState
from components.card_types import CardType
from constants.phases import TurnPhase
from constants.types import BRICK, GENERIC, LAMB, ROCK, TREE, WHEAT
from core.construction_manager import ConstructionManager
from core.scene_manager import SceneManager
from core.trade import BankTrade, PlayerTrade, TradeOffer
from core.turn_manager import TurnManager
from models.player import Player
from systems.achievements import AchievementsManager
from systems.bot_ai import BotDecisionMaker
from systems.card_manager import CardManager
from systems.longest_road import calculate_longest_road


def add_resources(player, resources):
    for resource, count in resources.items():
        player.inventory.add(resource, count)


def make_player(pid=1, name="P"):
    return Player(pid, name, (pid, pid, pid))


def test_scene_manager_stack_operations():
    manager = SceneManager()
    a, b = object(), object()

    assert manager.current is None
    manager.push(a)
    manager.replace(b)
    assert manager.current is b
    manager.pop()
    manager.pop()
    assert manager.current is None


def test_bank_trade_ratios_execute_and_failures():
    player = make_player()
    other = make_player(2, "Other")
    h1 = SimpleNamespace(owner=player)
    h2 = SimpleNamespace(owner=other)
    generic_port = SimpleNamespace(house1=h1, house2=h2, type=GENERIC, ratio=3)
    brick_port = SimpleNamespace(house1=h1, house2=h2, type=BRICK, ratio=2)
    closed_port = SimpleNamespace(house1=SimpleNamespace(owner=other), house2=SimpleNamespace(owner=other), type=TREE, ratio=2)

    assert BankTrade.get_ratio(player, BRICK, [closed_port, generic_port, brick_port]) == 2
    assert BankTrade.get_ratio(player, TREE, [closed_port, generic_port]) == 3
    assert BankTrade.get_ratio(player, ROCK, []) == 4

    add_resources(player, {BRICK: 3})
    assert BankTrade.can_execute(player, BRICK, 2, WHEAT, [brick_port])
    assert not BankTrade.can_execute(player, BRICK, 1, WHEAT, [brick_port])
    assert not BankTrade.can_execute(player, TREE, 4, WHEAT, [])
    assert BankTrade.execute(player, BRICK, 2, WHEAT)
    assert player.inventory.get_count(BRICK) == 1
    assert player.inventory.get_count(WHEAT) == 1
    assert not BankTrade.execute(player, BRICK, 4, WHEAT)


def test_player_trade_can_propose_accept_and_execute():
    proposer = make_player(1, "Proposer")
    target = make_player(2, "Target")
    add_resources(proposer, {BRICK: 2})
    add_resources(target, {WHEAT: 1})

    offer = TradeOffer(proposer, target, {BRICK: 2}, {WHEAT: 1})
    assert PlayerTrade.can_propose(offer)
    assert PlayerTrade.can_accept(offer)
    assert PlayerTrade.execute(offer)
    assert proposer.inventory.get_count(WHEAT) == 1
    assert target.inventory.get_count(BRICK) == 2

    impossible = TradeOffer(proposer, target, {ROCK: 1}, {LAMB: 1})
    assert not PlayerTrade.execute(impossible)
    assert PlayerTrade.can_propose(TradeOffer(proposer, target, {}, {}))
    assert PlayerTrade.can_accept(TradeOffer(proposer, target, {}, {}))


def test_construction_manager_validates_board_before_buying():
    player = make_player()
    board = MagicMock()
    manager = ConstructionManager(board)
    path = MagicMock()
    house = MagicMock()
    board.get_path.return_value = path
    board.get_intersection.return_value = house

    board.is_valid_road_connection.return_value = False
    assert not manager.attempt_build_road(player, "path")

    board.is_valid_road_connection.return_value = True
    add_resources(player, {BRICK: 1, TREE: 1})
    assert manager.attempt_build_road(player, "path")
    path.occupy.assert_called_once_with(player)

    board.respects_distance_rule.return_value = False
    assert not manager.attempt_build_settlement(player, "i")

    board.respects_distance_rule.return_value = True
    board.has_connecting_road.return_value = False
    assert not manager.attempt_build_settlement(player, "i")

    board.has_connecting_road.return_value = True
    add_resources(player, {BRICK: 1, TREE: 1, LAMB: 1, WHEAT: 1})
    assert manager.attempt_build_settlement(player, "i")
    house.build_settlement.assert_called_once_with(player)

    house.has_player_settlement.return_value = False
    assert not manager.attempt_upgrade_to_city(player, "i")
    house.has_player_settlement.return_value = True
    add_resources(player, {ROCK: 3, WHEAT: 2})
    assert manager.attempt_upgrade_to_city(player, "i")
    house.upgrade_to_city.assert_called_once()


def test_turn_manager_setup_phases_dice_and_victory():
    players = [make_player(1), make_player(2)]
    with patch("core.turn_manager.random.shuffle", lambda seq: None):
        manager = TurnManager(players)

    assert manager.current_player is players[0]
    manager.setup_record_house()
    manager.setup_record_road()
    assert manager.setup_turn_complete()
    manager.next_turn()
    assert manager.current_player is players[1]

    while manager.is_setup_phase:
        manager.next_turn()
    assert manager.current_phase == TurnPhase.DICE

    with patch("core.turn_manager.random.randint", side_effect=[3, 4]):
        assert manager.roll_dice() == (3, 4)
    assert manager.dice_sum == 7
    manager.next_phase()
    assert manager.current_phase == TurnPhase.CONSTRUCTION
    manager.next_phase()
    assert manager.current_phase == TurnPhase.DICE

    players[0].settlements_count = 10
    assert manager.check_victory() is players[0]


def test_turn_manager_buy_development_card_success_empty_and_insufficient():
    player = make_player()
    with patch("core.turn_manager.random.shuffle", lambda seq: None):
        manager = TurnManager([player])
    manager.is_setup_phase = False
    manager.development_cards = ["knight"]
    add_resources(player, {ROCK: 1, WHEAT: 1, LAMB: 1})

    assert manager.buy_development_card()
    assert player.development_cards == ["knight"]
    assert not manager.buy_development_card()

    add_resources(player, {ROCK: 1, WHEAT: 1, LAMB: 1})
    manager.development_cards = []
    assert not manager.buy_development_card()


class DummyRoad:
    def __init__(self, a, b, owner):
        self.house_a = a
        self.house_b = b
        self.owner = owner


def road_between(a, b, owner):
    return DummyRoad(a, b, owner)


class RoadHouse:
    def __init__(self, owner=None):
        self.owner = owner


def test_longest_road_handles_chains_branches_blocks_and_empty_sets():
    player = make_player()
    other = make_player(2)
    houses = [RoadHouse() for _ in range(5)]
    roads = [road_between(houses[i], houses[i + 1], player) for i in range(4)]

    assert calculate_longest_road(player, roads) == 4
    assert calculate_longest_road(other, roads) == 0

    houses[2].owner = other
    assert calculate_longest_road(player, roads) == 2


def test_achievements_award_and_transfer_longest_road_and_largest_army(monkeypatch):
    p1, p2 = make_player(1), make_player(2)
    manager = AchievementsManager([p1, p2])

    lengths = {p1: 5, p2: 4}
    monkeypatch.setattr("systems.achievements.calculate_longest_road", lambda player, roads: lengths[player])
    manager.update_longest_road([])
    assert p1.has_longest_road

    lengths[p2] = 6
    manager.update_longest_road([])
    assert not p1.has_longest_road
    assert p2.has_longest_road

    p1.knights_played = 3
    p2.knights_played = 2
    manager.update_largest_army()
    assert p1.has_largest_army
    p2.knights_played = 4
    manager.update_largest_army()
    assert not p1.has_largest_army
    assert p2.has_largest_army


def test_card_manager_buy_activate_errors_and_legacy_player_support(monkeypatch):
    player = make_player()
    manager = CardManager([player])
    add_resources(player, {ROCK: 1, LAMB: 1, WHEAT: 1})

    monkeypatch.setattr("systems.card_manager.DEVELOPMENT_CARDS", ["knight"])
    monkeypatch.setattr("systems.card_manager.random.choice", lambda choices: KnightCard)
    assert manager.attempt_buy_card(player)
    assert isinstance(player.development_cards[0], KnightCard)

    legacy = SimpleNamespace(inventory=player.inventory)
    manager._ensure_player_cards(legacy)
    assert legacy.development_cards == []
    assert not legacy.played_development_card_this_turn

    bad_card = BaseCard("Bad", card_type=CardType.KNIGHT, owner=player)
    bad_card.state = CardState.READY
    bad_card.bought_this_turn = False
    bad_card.activate = MagicMock(side_effect=RuntimeError("boom"))
    assert not manager.attempt_activate_card(player, bad_card)


def test_base_and_progress_cards_validate_activation_paths():
    player = make_player()
    card = BaseCard("Base", card_type=CardType.KNIGHT, owner=player)
    card.bought_this_turn = False
    card.state = CardState.READY
    assert card.activate()
    assert card.state == CardState.USED
    assert not card.can_activate(False)[0]

    locked = BaseCard("Locked", card_type=CardType.KNIGHT, owner=player)
    try:
        locked.activate()
    except RuntimeError as exc:
        assert "Cannot activate" in str(exc)

    progress = YearOfPlentyCard(owner=player)
    progress.discard()
    assert progress.state == CardState.USED

    road_card = RoadBuildingCard(owner=player)
    road_card.state = CardState.READY
    road_card.bought_this_turn = False
    try:
        road_card.activate(tabletop=None, edges=[])
    except ValueError as exc:
        assert "Road Building" in str(exc)


def test_bot_decisions_cover_trades_builds_robber_and_discards(monkeypatch):
    bot_player = make_player(1)
    opponent = make_player(2)
    decider = BotDecisionMaker(bot_player)

    offer = TradeOffer(opponent, bot_player, {WHEAT: 1}, {BRICK: 1})
    assert not decider.should_accept_trade_offer(offer)
    add_resources(bot_player, {BRICK: 1, TREE: 8, LAMB: 1})
    assert decider.should_accept_trade_offer(offer)

    add_resources(bot_player, {ROCK: 3, WHEAT: 2, LAMB: 1})
    bot_player.turns_since_last_dev_card = 3
    assert decider.should_build_road()
    assert decider.should_build_settlement()
    assert decider.should_build_city() is False
    bot_player.settlements_count = 1
    assert decider.should_build_city()
    assert decider.should_buy_development_card(turn_number=5)

    generic_port = SimpleNamespace(
        house1=SimpleNamespace(owner=bot_player),
        house2=SimpleNamespace(owner=None),
        type=GENERIC,
        ratio=3,
    )
    assert decider.get_bank_trade([generic_port]) == (TREE, 3, BRICK)
    assert decider.should_make_4_for_3_trade() == (TREE, 3, BRICK, 2)

    robber_house = SimpleNamespace(owner=opponent, level=2)
    tile = SimpleNamespace(extract_houses=lambda: [robber_house])
    bot_player.knights_played = 2
    assert decider.should_play_knight(tile)
    assert decider.select_robber_tile([tile]) is tile

    monkeypatch.setattr("systems.bot_ai.random.choice", lambda seq: seq[0])
    assert decider.select_robber_victim([opponent]) is opponent
    assert decider.select_robber_victim([]) is None
    assert decider.select_discard_resources(3)[TREE] == 3
