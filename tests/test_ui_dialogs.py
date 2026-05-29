import pytest

from components.year_of_plenty_dialog import YearOfPlentyDialog
from components.monopoly_dialog import MonopolyDialog
from components.road_building_dialog import RoadBuildingDialog
from models.bank import Bank
from models.player import Player
from components.road import Road


def test_year_of_plenty_dialog_confirm_calls_callback():
    p = Player(1, "P1", (10, 10, 10))
    bank = Bank(initial_count=2)
    captured = []

    def on_confirm(resources):
        captured.extend(resources)

    dlg = YearOfPlentyDialog(p, bank, on_confirm=on_confirm)
    # manually pick two resources
    keys = list(dlg.selection.keys())
    dlg.selection[keys[0]] = 1
    dlg.selection[keys[1]] = 1
    assert dlg._total_selected() == 2
    dlg._do_confirm()
    assert len(captured) == 2
    assert set(captured) == {keys[0], keys[1]}


def test_road_try_build_force_free():
    p = Player(1, "P1", (10, 10, 10))
    r = Road(((0, 0), (10, 0)))
    before = p.roads_count
    ok = r.try_build(p, all_roads=set(), force_free=True)
    assert ok is True
    assert r.owner is p
    assert p.roads_count == before + 1


def test_road_building_dialog_selection_clamps_to_two():
    p = Player(1, "P1", (10, 10, 10))
    r1 = Road(((0, 0), (10, 0)))
    r2 = Road(((20, 0), (30, 0)))
    r3 = Road(((40, 0), (50, 0)))

    class T:
        pass

    tabletop = T()
    tabletop.roads = set([r1, r2, r3])

    dlg = RoadBuildingDialog(p, tabletop)
    # simulate accidental large selection
    dlg.selected = [r1, r2, r3]
    dlg.update(0)
    assert len(dlg.selected) == 2


def test_monopoly_in_game_accepts_string_resource_mapping():
    # lazy import Game to ensure heavy setup happens inside test
    from scenes.game import Game
    from components.base_card import MonopolyCard
    from components.card_states import CardState
    from constants.types import BRICK

    g = Game(None)
    owner = g.current_player
    # give others some bricks
    for p in g.players:
        if p is not owner:
            p.inventory.add(BRICK, 1)

    card = MonopolyCard()
    owner.add_development_card(card)
    # mark card ready
    card.bought_this_turn = False
    card.state = CardState.READY
    g._pending_card = card

    # call resolver with string name 'brick'
    g._resolve_monopoly('brick')
    # owner should have collected from other players
    assert owner.inventory.get_count(BRICK) >= 2


def test_road_building_dialog_cannot_select_built_adjacent_road():
    import types
    import pygame
    # ensure the event constant exists in the test environment
    setattr(pygame, 'MOUSEBUTTONDOWN', getattr(pygame, 'MOUSEBUTTONDOWN', 1))
    # ensure common constants exist in the test pygame shim
    setattr(pygame, 'KEYDOWN', getattr(pygame, 'KEYDOWN', 2))
    setattr(pygame, 'K_d', getattr(pygame, 'K_d', 100))

    p1 = Player(1, "P1", (10, 10, 10))
    p2 = Player(2, "P2", (20, 20, 20))

    r1 = Road(((0, 0), (10, 0)))
    r2 = Road(((10, 0), (20, 0)))
    # simulate adjacency via shared house placeholder
    H = object()
    r1.house_b = H
    r2.house_a = H

    # r2 already has an owner (built)
    r2.owner = p2

    class T:
        pass

    tabletop = T()
    tabletop.roads = set([r1, r2])

    dlg = RoadBuildingDialog(p1, tabletop)
    # pre-select r1 so adjacency-based selection could otherwise allow r2
    dlg.selected = [r1]

    # click near r2 center
    x = (r2.x0 + r2.x1) / 2
    y = (r2.y0 + r2.y1) / 2
    evt = types.SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(x, y))
    dlg.handle_event(evt)

    # r2 must NOT be selectable because it already has an owner
    assert r2 not in dlg.selected


def test_clicking_locked_development_shows_toast():
    from scenes.game import Game
    from components.base_card import BaseCard
    from components.card_types import CardType
    import types
    import pygame

    g = Game(None)
    owner = g.current_player

    # add a locked card (bought this turn)
    card = BaseCard("Knight", "Desc", CardType.KNIGHT)
    owner.add_development_card(card)

    # show HUD and set player reference
    g.show_development_cards = True
    g.development_display.set_player(owner)

    # click center of first card slot
    x = int(g.development_display.x + g.development_display.card_width / 2)
    y = int(g.development_display.y + g.development_display.card_height / 2)
    setattr(pygame, 'MOUSEBUTTONDOWN', getattr(pygame, 'MOUSEBUTTONDOWN', 1))
    # ensure KEYDOWN and K_d exist on fake pygame used in tests
    setattr(pygame, 'KEYDOWN', getattr(pygame, 'KEYDOWN', 2))
    setattr(pygame, 'K_d', getattr(pygame, 'K_d', 100))
    evt = types.SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(x, y))
    g.handle_event(evt)

    # toast should be shown explaining it's not ready
    assert g.toast_manager.items, "Expected a toast to be shown"
    last = g.toast_manager.items[-1][0]
    assert "não está pronta" in last or "Já jogou" in last or "Carta já foi utilizada" in last


def test_dev_toggle_button_same_size_and_no_overlap():
    from scenes.game import Game

    g = Game(None)
    # development toggle should have same width as other HUD buttons
    assert g.btn_dev_cards.rect.width == g.btn_bank.rect.width
    # buttons in second row should not overlap horizontally
    assert g.btn_buy_card.rect.left >= g.btn_dev_cards.rect.right


def test_monopoly_dialog_has_no_fullscreen_overlay():
    from scenes.game import Game
    from components.base_card import MonopolyCard
    from components.card_states import CardState
    from components.monopoly_dialog import MonopolyDialog

    g = Game(None)
    owner = g.current_player
    card = MonopolyCard()
    owner.add_development_card(card)
    card.bought_this_turn = False
    card.state = CardState.READY

    # play the card and check active dialog overlay setting
    g._play_development_card(card)
    assert isinstance(g.active_dialog, MonopolyDialog)
    assert getattr(g.active_dialog, 'overlay_fullscreen', False) is False
