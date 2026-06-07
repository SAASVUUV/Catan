from types import SimpleNamespace
from unittest.mock import MagicMock, mock_open

import pytest
import pygame

from components.base_card import KnightCard, MonopolyCard, RoadBuildingCard, YearOfPlentyCard
from components.card_states import CardState
from constants.phases import TurnPhase
from constants.types import BRICK, ROCK, TREE, WHEAT
from core.trade import TradeOffer
from models.player import Player


def event(event_type, **kwargs):
    return SimpleNamespace(type=event_type, **kwargs)


def surface():
    return pygame.Surface((800, 600))


def ready(card, owner):
    owner.add_development_card(card)
    card.state = CardState.READY
    card.bought_this_turn = False
    return card


def test_card_view_handles_states_hover_selection_and_tooltips():
    from components.card_states import CardState
    from scenes.card_view import CardView

    canvas = surface()
    card = SimpleNamespace(name="Knight", description="Move robber", state=CardState.READY)
    view = CardView(card, 10, 80)

    view.handle_event(event(pygame.MOUSEMOTION, pos=(12, 82)))
    assert view.is_hovered
    view.is_selected = True
    view.render(canvas)

    card.state = CardState.LOCKED
    view.render(canvas)
    card.state = CardState.USED
    view.render(canvas)

    view.handle_event(event(pygame.MOUSEMOTION, pos=(400, 400)))
    assert not view.is_hovered


def test_main_menu_start_config_quit_update_and_render(monkeypatch):
    from scenes.main_menu import MainMenu

    manager = MagicMock()
    game_scene = object()
    config_scene = object()
    quit_events = []
    monkeypatch.setattr("scenes.main_menu.game.Game", lambda manager, bot_list=None: ("game", tuple(bot_list)))
    monkeypatch.setattr("scenes.main_menu.configurations.Configurations", lambda manager: config_scene)
    monkeypatch.setattr(pygame.event, "post", lambda evt: quit_events.append(evt))

    menu = MainMenu(manager)
    menu.slots[3].is_bot = True
    menu.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.btn_start.rect.center))
    manager.replace.assert_called_with(("game", (4,)))

    menu.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.btn_config.rect.center))
    manager.replace.assert_called_with(config_scene)

    menu.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=menu.btn_quit.rect.center))
    assert quit_events and quit_events[-1].type == pygame.QUIT

    menu.handle_event(event(pygame.QUIT))
    menu.update(0.016)
    menu.render(surface())


def test_configurations_load_apply_save_back_and_render(monkeypatch):
    from scenes.configurations import Configurations

    class FakeSound:
        def __init__(self):
            self.master_volume = 0.2
            self.music_volume = 0.3
            self.sfx_volume = 0.4
            self.calls = []

        def set_master_volume(self, value):
            self.calls.append(("master", value))

        def set_music_volume(self, value):
            self.calls.append(("music", value))

        def set_sfx_volume(self, value):
            self.calls.append(("sfx", value))

        def save_settings(self):
            self.calls.append(("save", None))

    fake = FakeSound()
    monkeypatch.setattr("scenes.configurations.SoundManager", lambda: fake)
    monkeypatch.setattr("scenes.configurations.MainMenu", lambda manager: ("menu", manager), raising=False)

    manager = MagicMock()
    config = Configurations(manager)
    assert config.slider_master_sound.get_value() == 0.2
    config.update(0.016)
    config.render(surface())
    config.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=config.btn_back.rect.center))
    manager.replace.assert_called()
    assert ("save", None) in fake.calls


def test_settings_menu_stub_methods_are_callable():
    from scenes.settings_menu import SettingsMenu

    menu = SettingsMenu(MagicMock())
    assert menu.enter() is None
    assert menu.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))) is None
    assert menu.update(0.016) is None
    assert menu.render(surface()) is None


def test_sound_manager_uses_mocks_for_file_io_and_mixer(monkeypatch):
    import utils.sound as sound_module

    sound_module.SoundManager._instance = None
    sound_module.SoundManager._sounds = {}
    data = '{"master_volume": 0.5, "music_volume": 0.25, "sfx_volume": 0.75}'
    monkeypatch.setattr(sound_module.os.path, "exists", lambda path: True)
    monkeypatch.setattr("builtins.open", mock_open(read_data=data))

    manager = sound_module.SoundManager()
    assert manager.master_volume == 0.5
    assert manager.music_volume == 0.25
    assert manager.sfx_volume == 0.75
    manager.play("invalid_action")
    manager.play("missing")
    manager.play_music("soundtrack", loops=1)
    manager.play_music("missing")
    manager.set_volume("invalid_action", 2)
    manager.set_master_volume(2)
    manager.set_music_volume(-1)
    manager.set_sfx_volume(0.4)
    manager.stop("invalid_action")
    manager.stop()
    manager.save_settings()
    manager.stop_music()

    sound_module.SoundManager._instance = None
    monkeypatch.setattr(sound_module.os.path, "exists", lambda path: False)
    sound_module.SoundManager()


def test_main_run_initializes_loop_and_exits(monkeypatch):
    import main

    monkeypatch.setattr(main, "MainMenu", lambda manager: SimpleNamespace(handle_event=lambda e: None, update=lambda dt: None, render=lambda s: None))
    monkeypatch.setattr(main, "SoundManager", lambda: SimpleNamespace(play_music=lambda *a, **k: None))
    monkeypatch.setattr(main.settings, "FULLSCREEN", False)
    monkeypatch.setattr(pygame.event, "get", lambda: [pygame.event.Event(pygame.QUIT)])
    monkeypatch.setattr(main.sys, "exit", lambda: (_ for _ in ()).throw(SystemExit))

    with pytest.raises(SystemExit):
        main.run()


def test_game_private_flows_cover_dialogs_trades_robber_and_cards(monkeypatch):
    from scenes.game import Game

    monkeypatch.setattr("scenes.game.SoundManager", lambda: SimpleNamespace(play=lambda *a, **k: None))
    game = Game(None)
    game.manager = MagicMock()
    current = game.current_player
    game.turn_manager.is_setup_phase = False
    game.turn_manager.current_phase = TurnPhase.COMMERCE

    assert game._can_trade()
    assert not game._can_build()
    game._open_bank_dialog()
    assert game.active_dialog is not None
    current.inventory.add(BRICK, 4)
    game._execute_bank_trade(BRICK, 4, WHEAT)
    assert game.active_dialog is None

    game._open_player_dialog()
    assert game.active_dialog is not None
    offer = TradeOffer(current, None, {}, {})
    game._show_offer_dialog(offer)
    assert game.pending_offer is offer
    game._show_next_target()
    assert game.active_dialog is not None or game.pending_targets

    acceptor = [p for p in game.players if p is not current][0]
    current.inventory.add(BRICK, 1)
    acceptor.inventory.add(WHEAT, 1)
    game._execute_player_trade(TradeOffer(current, acceptor, {BRICK: 1}, {WHEAT: 1}), acceptor)
    assert game.pending_offer is None

    game._discard_queue = []
    game._open_next_discard_dialog()
    assert game.awaiting_robber_tile

    game._discarding_player = current
    current.inventory.add(BRICK, 2)
    game._confirm_discard({BRICK: 1})
    assert current.inventory.get_count(BRICK) >= 1

    old_tile = game.tabletop.robber_tile
    game._handle_robber_tile_click((old_tile.x, old_tile.y))
    assert game.toast_manager.items
    new_tile = next(tile for tile in game.tabletop.tiles if tile is not old_tile)
    game._handle_robber_tile_click((new_tile.x, new_tile.y))
    assert not game.awaiting_robber_tile

    victim = acceptor
    victim.inventory.add(TREE, 1)
    game._steal_random_resource(victim)
    game._skip_robber_steal()

    knight = ready(KnightCard(), current)
    game._play_development_card(knight)
    assert current.knights_played >= 1

    current.played_development_card_this_turn = False
    plenty = ready(YearOfPlentyCard(), current)
    game._play_development_card(plenty)
    assert game.active_dialog is not None
    game._pending_card = plenty
    game.bank.add(BRICK, 2)
    game._resolve_year_of_plenty([BRICK, BRICK])

    current.played_development_card_this_turn = False
    monopoly = ready(MonopolyCard(), current)
    game._pending_card = monopoly
    game._resolve_monopoly("invalid")
    current.played_development_card_this_turn = False
    monopoly = ready(MonopolyCard(), current)
    game._pending_card = monopoly
    game._resolve_monopoly(BRICK)

    current.played_development_card_this_turn = False
    road_card = ready(RoadBuildingCard(), current)
    road = next(iter(game.tabletop.roads))
    game._pending_card = road_card
    game._resolve_road_building([road])

    current.settlements_count = 10
    game._update_turn_state()
    assert game.active_dialog is not None


def test_game_dice_roll_seven_and_normal_paths(monkeypatch):
    from scenes.game import Game

    monkeypatch.setattr("scenes.game.SoundManager", lambda: SimpleNamespace(play=lambda *a, **k: None))
    game = Game(None)
    game.turn_manager.is_setup_phase = False

    monkeypatch.setattr(game.turn_manager, "roll_dice", lambda: setattr(game.turn_manager, "last_dice_roll", (3, 4)))
    game._do_dice_roll()
    assert game.awaiting_robber_tile or game.active_dialog is not None

    game.awaiting_robber_tile = False
    game.active_dialog = None
    monkeypatch.setattr(game.turn_manager, "roll_dice", lambda: setattr(game.turn_manager, "last_dice_roll", (2, 3)))
    game._do_dice_roll()
    assert game.turn_manager.dice_sum == 5
