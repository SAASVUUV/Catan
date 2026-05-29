import pytest

from models.player import Player
from components.base_card import YearOfPlentyCard, MonopolyCard, RoadBuildingCard
from systems.card_manager import CardManager
from models.bank import Bank
from components.road import Road
from constants.types import BRICK, TREE, WHEAT


def test_year_of_plenty_takes_from_bank_and_gives_to_player():
    p1 = Player(1, "P1", (10, 10, 10))
    manager = CardManager([p1])
    card = YearOfPlentyCard()
    p1.add_development_card(card)
    manager.on_turn_start(p1)

    bank = Bank(initial_count=2)
    # resolve giving one BRICK and one WHEAT
    success = manager.attempt_activate_card(p1, card, resources=[BRICK, WHEAT], bank=bank)
    assert success is True
    assert p1.inventory.get_count(BRICK) == 1
    assert p1.inventory.get_count(WHEAT) == 1
    assert bank.get_count(BRICK) == 1
    assert bank.get_count(WHEAT) == 1


def test_monopoly_collects_from_other_players():
    p1 = Player(1, "P1", (10, 10, 10))
    p2 = Player(2, "P2", (20, 20, 20))
    p3 = Player(3, "P3", (30, 30, 30))
    manager = CardManager([p1, p2, p3])

    # give others some BRICK
    p2.inventory.add(BRICK, 2)
    p3.inventory.add(BRICK, 1)

    card = MonopolyCard()
    p1.add_development_card(card)
    manager.on_turn_start(p1)

    success = manager.attempt_activate_card(p1, card, resource=BRICK)
    assert success is True
    # p1 should have collected 3 bricks
    assert p1.inventory.get_count(BRICK) == 3
    assert p2.inventory.get_count(BRICK) == 0
    assert p3.inventory.get_count(BRICK) == 0


def test_road_building_places_two_roads_without_cost():
    p1 = Player(1, "P1", (10, 10, 10))
    manager = CardManager([p1])

    # create two isolated road edges (simple coords)
    r1 = Road(((0, 0), (10, 0)))
    r2 = Road(((20, 0), (30, 0)))

    card = RoadBuildingCard()
    p1.add_development_card(card)
    manager.on_turn_start(p1)

    # dummy tabletop exposing roads set
    class T:
        pass

    tabletop = T()
    tabletop.roads = set([r1, r2])

    success = manager.attempt_activate_card(p1, card, tabletop=tabletop, edges=[r1, r2])
    assert success is True
    assert r1.owner is p1
    assert r2.owner is p1
    assert p1.roads_count == 2


def test_road_building_respects_stock_limit_builds_only_one_if_one_left():
    p1 = Player(1, "P1", (10, 10, 10))
    manager = CardManager([p1])

    # edges
    r1 = Road(((0, 0), (10, 0)))
    r2 = Road(((20, 0), (30, 0)))

    card = RoadBuildingCard()
    p1.add_development_card(card)
    manager.on_turn_start(p1)

    # simulate player already having 14 roads (one remaining)
    for _ in range(14):
        p1.add_road()

    class T:
        pass

    tabletop = T()
    tabletop.roads = set([r1, r2])

    success = manager.attempt_activate_card(p1, card, tabletop=tabletop, edges=[r1, r2])
    assert success is True
    # only one road should have been placed because only one piece remained
    built = sum(1 for r in (r1, r2) if r.owner is p1)
    assert built == 1
    assert p1.roads_count == 15


def test_road_building_no_stock_has_no_effect():
    p1 = Player(1, "P1", (10, 10, 10))
    manager = CardManager([p1])

    r1 = Road(((0, 0), (10, 0)))
    r2 = Road(((20, 0), (30, 0)))

    card = RoadBuildingCard()
    p1.add_development_card(card)
    manager.on_turn_start(p1)

    # simulate player having no road pieces left
    for _ in range(15):
        p1.add_road()

    class T:
        pass

    tabletop = T()
    tabletop.roads = set([r1, r2])

    success = manager.attempt_activate_card(p1, card, tabletop=tabletop, edges=[r1, r2])
    assert success is True
    # no roads placed
    assert r1.owner is None and r2.owner is None
    assert p1.roads_count == 15


def test_year_of_plenty_allows_building_same_turn():
    p = Player(1, "P1", (10, 10, 10))
    manager = CardManager([p])

    # player has one TREE but no BRICK, so needs Year of Plenty to complete road cost
    from constants.types import BRICK, TREE
    p.inventory.add(TREE, 1)

    card = YearOfPlentyCard()
    p.add_development_card(card)
    manager.on_turn_start(p)

    bank = Bank(initial_count=5)
    # activate and request BRICK + TREE
    success = manager.attempt_activate_card(p, card, resources=[BRICK, TREE], bank=bank)
    assert success is True

    # Now the player should be able to buy a road immediately using the resources
    bought = p.buy_road()
    assert bought is True
    assert p.roads_count == 1
