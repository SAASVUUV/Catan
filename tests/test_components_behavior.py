from types import SimpleNamespace

import pygame

from components.bank_trade_dialog import BankTradeDialog
from components.button import Button
from components.checkbox import Checkbox
from components.circle import Circle
from components.development_display import DevelopmentDisplay
from components.dice import Dice
from components.house import House
from components.label import Label
from components.modal import Modal
from components.monopoly_dialog import MonopolyDialog
from components.player_list_panel import PlayerListPanel
from components.player_trade_dialog import PlayerTradeDialog, TradeOfferDialog
from components.resource_display import ResourceDisplay
from components.robber_dialogs import DiscardResourcesDialog, RobberStealDialog
from components.road import Road
from components.selection_icons import PlayerSlot, draw_bot_icon, draw_person_icon
from components.slider import Slider
from components.text import Text
from components.turn_controls import TurnControls
from components.year_of_plenty_dialog import YearOfPlentyDialog
from constants.phases import TurnPhase
from constants.types import BRICK, LAMB, ROCK, TREE, WHEAT
from core.trade import TradeOffer
from models.bank import Bank
from models.player import Player
from ui.toast import ToastManager
from utils.mymath import take_third_point
from utils.myrandom import takesome
from utils.sprites import SpriteLoader


def event(event_type, **kwargs):
    return SimpleNamespace(type=event_type, **kwargs)


def surface(size=(800, 600)):
    return pygame.Surface(size)


def player_with(resources=None, pid=1):
    player = Player(pid, f"P{pid}", (pid * 10, pid * 10, pid * 10))
    for resource, count in (resources or {}).items():
        player.inventory.add(resource, count)
    return player


def test_circle_dice_text_label_and_toast_render_paths(monkeypatch):
    canvas = surface()
    c1 = Circle(10, 10, 5, (1, 2, 3))
    c2 = Circle(14, 10, 5, (1, 2, 3))
    assert c1.collidecircle(c2)
    assert c1.collidepoint((10, 14))
    c1.render(canvas)

    dice = Dice(10, 10, size=40)
    assert dice._get_dot_positions(0, 0, 0) == []
    dice.set_values(1, 6)
    dice.render(canvas)
    dice.hide()
    dice.render(canvas)

    Text("hello", 12, (0, 0, 0), (10, 10)).render(canvas)
    Text("hello", 12, (0, 0, 0), (10, 10)).render_center(canvas)
    Label("label", 0, 0).render(canvas)

    now = [100.0]
    monkeypatch.setattr("ui.toast.time.time", lambda: now[0])
    toast = ToastManager()
    toast.show("msg", duration=1)
    toast.render(canvas)
    now[0] = 102.0
    toast.update()
    assert toast.items == []


def test_button_checkbox_slider_modal_and_turn_controls_events(monkeypatch):
    canvas = surface()
    clicks = []
    button = Button(0, 0, 100, 40, "OK", on_click=lambda: clicks.append("clicked"), shadow=True)
    assert button.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10)))
    button.update()
    button.render(canvas)
    assert clicks
    button.enabled = False
    assert not button.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10)))
    button.render(canvas)

    checkbox = Checkbox(0, 0, 20)
    checkbox.handle_event(event(pygame.MOUSEMOTION, pos=(1, 1)))
    assert checkbox.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(1, 1)))
    assert checkbox.check

    slider = Slider(0, 0, 100, 10)
    slider.set_value(2)
    assert slider.get_value() == 1.0
    slider.set_value(-1)
    assert slider.get_value() == 0.0
    slider.hovered = True
    slider.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5)))
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (55, 0))
    slider.update()
    assert slider.get_value() == 0.55
    slider.handle_event(event(pygame.MOUSEBUTTONUP, button=1, pos=(55, 0)))
    slider.render(canvas)

    modal = Modal(100, 80, "Title")
    assert not modal.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))
    modal.show()
    assert modal.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))
    modal.render(canvas)
    modal.hide()
    modal.render(canvas)

    controls = TurnControls(0, 0, 200)
    assert controls.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10))) is None
    controls.set_state(TurnPhase.DICE, (2, 3), is_setup=False)
    assert controls.dice.visible
    assert controls.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=controls.btn_roll.rect.center)) == "roll"
    controls.set_state(TurnPhase.COMMERCE, None, is_setup=False)
    assert controls.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=controls.btn_next.rect.center)) == "next_phase"
    controls.set_state(TurnPhase.CONSTRUCTION, None, is_setup=False)
    assert controls.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=controls.btn_end.rect.center)) == "end_turn"
    controls.set_timer(10)
    controls.update()
    controls.render(canvas)


def test_house_build_upgrade_distance_rule_and_road_building(monkeypatch):
    monkeypatch.setattr("components.house.SoundManager", lambda: SimpleNamespace(play=lambda *_: None))
    monkeypatch.setattr("components.road.SoundManager", lambda: SimpleNamespace(play=lambda *_: None))
    canvas = surface()

    player = player_with()
    house = House((10, 10))
    assert house.try_build(player)
    assert house.owner is player
    assert player.settlements_count == 1

    blocked = House((20, 20))
    blocked.adjacent_houses.add(house)
    assert not blocked.try_build(player)
    assert blocked._invalid_timer > 0
    blocked.update(1.0)
    blocked.render(canvas)

    player.settlements_count = 2
    paid_house = House((30, 30))
    player.inventory.add(BRICK, 1)
    player.inventory.add(TREE, 1)
    player.inventory.add(LAMB, 1)
    player.inventory.add(WHEAT, 1)
    assert paid_house.try_build(player)

    player.inventory.add(ROCK, 3)
    player.inventory.add(WHEAT, 2)
    assert paid_house.try_build(player)
    assert paid_house.level == 2
    assert not paid_house.try_build(player_with(pid=2))

    road = Road(((0, 0), (10, 0)))
    assert road.try_build(player_with())
    road.render(canvas)
    assert road.collidepoint((5, 0))
    assert not road.collidepoint((5, 20))

    owner = player_with(pid=3)
    owner.settlements_count = 2
    owner.roads_count = 2
    normal_road = Road(((10, 0), (20, 0)))
    normal_road.house_a = SimpleNamespace(owner=None)
    normal_road.house_b = SimpleNamespace(owner=None)
    assert not normal_road.try_build(owner, all_roads=set())

    connected = Road(((20, 0), (30, 0)))
    shared = SimpleNamespace(owner=owner)
    connected.house_a = shared
    connected.house_b = SimpleNamespace(owner=None)
    owner.inventory.add(BRICK, 1)
    owner.inventory.add(TREE, 1)
    assert connected.try_build(owner, all_roads=set())
    connected.update(0.2)


def test_resource_player_and_development_displays(monkeypatch):
    canvas = surface()
    player = player_with({BRICK: 1})

    resources = ResourceDisplay(10, 10)
    assert resources.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))) is False
    resources.update(0)
    resources.render(canvas)
    resources.set_player(player)
    resources.render(canvas)

    player.has_longest_road = True
    player.has_largest_army = True
    panel = PlayerListPanel(0, 0, 220, [player])
    panel.set_current_player(player)
    panel.render(canvas)

    from components.base_card import BaseCard, KnightCard, UniversityCard

    display = DevelopmentDisplay(10, 10)
    assert display._groups() == []
    display.render(canvas)
    locked = BaseCard("Locked", card_type=None)
    ready = KnightCard(owner=player)
    ready.state = "not-ready"
    ready.bought_this_turn = True
    vp = UniversityCard(owner=player)
    player.development_cards = [locked, ready, vp, None]
    display.set_player(player)
    groups = display._groups()
    assert len(groups) == 3
    result = display.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(12, 12)))
    assert result is not None
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (12, 12))
    display.update()
    display.render(canvas)


def test_dialogs_handle_selection_confirmation_cancel_and_render():
    canvas = surface()
    player = player_with({BRICK: 4, WHEAT: 1})
    bank = Bank(initial_count=1)

    captured = []
    yop = YearOfPlentyDialog(player, bank, on_confirm=lambda res: captured.append(res), on_cancel=lambda: captured.append("cancel"))
    assert not yop.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))
    yop.show()
    resource, rect = next(iter(_resource_rects(yop)))
    assert yop.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
    assert yop.selection[resource] == 1
    yop.selection[WHEAT] = 1
    yop.update(0)
    assert yop.confirm_btn.enabled
    yop.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=yop.confirm_btn.rect.center))
    assert captured and isinstance(captured[0], list)
    yop.render(canvas)

    mono_capture = []
    monopoly = MonopolyDialog(player, on_confirm=mono_capture.append, on_cancel=lambda: mono_capture.append("cancel"))
    monopoly.show()
    resource, rect = next(iter(_resource_rects(monopoly, top_offset=40)))
    monopoly.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
    assert mono_capture == [resource]
    monopoly.show()
    monopoly.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))
    assert mono_capture[-1] == "cancel"
    monopoly.render(canvas)

    bank_calls = []
    bank_dialog = BankTradeDialog(player, [], lambda *args: bank_calls.append(args), lambda: bank_calls.append("cancel"))
    bank_dialog.show()
    bank_dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=bank_dialog.give_buttons[3]["rect"].center))
    bank_dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=bank_dialog.receive_buttons[4]["rect"].center))
    assert bank_dialog._can_trade()
    bank_dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=bank_dialog.btn_confirm.rect.center))
    assert bank_calls[-1] == (BRICK, 4, WHEAT)
    bank_dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=bank_dialog.btn_cancel.rect.center))
    bank_dialog.render(canvas)


def test_player_trade_and_robber_dialogs():
    canvas = surface()
    proposer = player_with({BRICK: 2})
    target = player_with({WHEAT: 1}, pid=2)

    proposed = []
    dialog = PlayerTradeDialog(proposer, [proposer, target], proposed.append, lambda: proposed.append("cancel"))
    assert not dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0)))
    dialog.show()
    dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=dialog.offer_rects[3]["rect"].center))
    dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=dialog.request_rects[4]["rect"].center))
    assert dialog._can_propose()
    dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=3, pos=dialog.offer_rects[3]["rect"].center))
    dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=dialog.offer_rects[3]["rect"].center))
    dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=dialog.btn_propose.rect.center))
    assert proposed and isinstance(proposed[-1], TradeOffer)
    dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=dialog.btn_cancel.rect.center))
    dialog.render(canvas)

    offer = TradeOffer(proposer, target, {BRICK: 1}, {WHEAT: 1})
    accepted = []
    offer_dialog = TradeOfferDialog(offer, target, lambda *args: accepted.append(args), lambda: accepted.append("reject"))
    offer_dialog.show()
    assert offer_dialog._res_name(999) == "?"
    offer_dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=offer_dialog.btn_accept.rect.center))
    assert accepted[-1] == (offer, target)
    offer_dialog.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=offer_dialog.btn_reject.rect.center))
    offer_dialog.render(canvas)

    discard_calls = []
    discard = DiscardResourcesDialog(proposer, 1, discard_calls.append)
    discard.show()
    res, rect = next(iter(discard._resource_rects()))
    discard.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center))
    discard.handle_event(event(pygame.MOUSEBUTTONDOWN, button=3, pos=rect.center))
    brick_rect = [r for r, rect in discard._resource_rects() if r == BRICK]
    assert brick_rect
    discard.selection[BRICK] = 1
    discard.update(0)
    discard.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=discard.confirm_btn.rect.center))
    assert discard_calls[-1] == {BRICK: 1}
    discard.render(canvas)

    robber_calls = []
    robber = RobberStealDialog([target], robber_calls.append, lambda: robber_calls.append("skip"))
    robber.show()
    robber.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=robber.buttons[0][1].rect.center))
    robber.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=robber.skip_btn.rect.center))
    robber.update(0)
    robber.render(canvas)
    assert target in robber_calls and "skip" in robber_calls


def test_selection_icons_sprite_loader_math_and_random(monkeypatch):
    canvas = surface()
    draw_person_icon(canvas, 10, 10, 20, (1, 1, 1))
    draw_bot_icon(canvas, 20, 20, 20, (1, 1, 1))

    slot = PlayerSlot(0, 0, 0)
    assert not slot.is_bot
    slot.on_mouse_click()
    assert slot.is_bot
    slot.handle_event(event(pygame.MOUSEBUTTONDOWN, button=1, pos=slot.rect.center))
    slot.update()
    slot.render(canvas)

    loader = SpriteLoader()
    assert loader.get_terrain_sprite(999, (10, 10)).get_size() == (10, 10)
    assert loader.get_port_sprite(999, (10, 10)).get_size() == (10, 10)
    assert loader.get_sprite("missing.png", (12, 12)).get_size() == (12, 12)
    assert loader.get_tinted_sprite("road", (255, 0, 0), (10, 10)).get_size() == (10, 10)

    assert take_third_point(0, 0, 2, 0)[0] == 1
    monkeypatch.setattr("utils.myrandom.randrange", lambda n: 1)
    values = [10, 20, 30]
    assert takesome(values) == 20
    assert values == [10, 30]


def _resource_rects(dialog, top_offset=50):
    from models.inventory import TRADEABLE_RESOURCES

    total_w = len(TRADEABLE_RESOURCES) * (dialog.card_width + dialog.card_spacing) - dialog.card_spacing
    start_x = dialog.rect.left + (dialog.width - total_w) // 2
    y = dialog.rect.top + top_offset
    for i, resource in enumerate(TRADEABLE_RESOURCES):
        x = start_x + i * (dialog.card_width + dialog.card_spacing)
        yield resource, pygame.Rect(x, y, dialog.card_width, dialog.card_height)
