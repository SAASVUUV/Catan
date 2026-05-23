import pygame
from .base_scene import BaseScene
from models.player import Player
from core.turn_manager import TurnManager
from components.tabletop import Tabletop
from components.button import Button
from components.resource_display import ResourceDisplay
from components.bank_trade_dialog import BankTradeDialog
from components.player_trade_dialog import PlayerTradeDialog, TradeOfferDialog
from components.player_list_panel import PlayerListPanel
from components.turn_controls import TurnControls
from core.trade import BankTrade, PlayerTrade
from constants.colors import RED, BLUE, GREEN, BLACK, YELLOW, SEA_BLUE
from constants.phases import TurnPhase
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Game(BaseScene):
    def __init__(self, manager=None):
        self.manager = manager
        self.players = [
            Player(1, "Player 1", RED),
            Player(2, "Player 2", BLUE),
            Player(3, "Player 3", GREEN),
            Player(4, "Player 4", YELLOW)
        ]
        self.turn_manager = TurnManager(self.players)
        self.turn_manager.shuffle_player_order()

        hex_radius = int(SCREEN_HEIGHT * 0.085)
        board_x = int(SCREEN_WIDTH * 0.2)
        board_y = int(SCREEN_HEIGHT * 0.15)
        self.tabletop = Tabletop(board_x, board_y, hex_radius)

        self._setup_ui()
        self.active_dialog = None
        self.pending_offer = None
        self.pending_targets = []
        self._update_turn_state()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    @property
    def current_player(self):
        return self.turn_manager.current_player

    def _setup_ui(self):
        scale = SCREEN_HEIGHT / 600.0
        margin = int(SCREEN_WIDTH * 0.02)
        bottom_margin = int(SCREEN_HEIGHT * 0.15)

        self.resource_display = ResourceDisplay(SCREEN_WIDTH * 0.2, SCREEN_HEIGHT - bottom_margin, scale)
        self.resource_display.set_player(self.current_player)

        btn_w = int(88 * scale)
        btn_h = int(33 * scale)
        btn_font = int(15 * scale)
        btn_x = int(SCREEN_WIDTH * 0.45)
        btn_y = SCREEN_HEIGHT - bottom_margin - 10
        btn_gap = int(10 * scale)
        self.btn_bank = Button(btn_x, btn_y, btn_w, btn_h, "Banco", font_size=btn_font)
        self.btn_trade = Button(btn_x, btn_y + btn_h + btn_gap, btn_w, btn_h, "Trocar", font_size=btn_font)

        panel_width = int(240 * scale)
        panel_width = max(200, min(panel_width, 350))
        self.player_list = PlayerListPanel(SCREEN_WIDTH - panel_width - margin, margin, panel_width, self.players, scale)

        turn_ctrl_height = int(140 * scale)
        self.turn_controls = TurnControls(SCREEN_WIDTH - panel_width - margin, SCREEN_HEIGHT - turn_ctrl_height - margin, panel_width, scale)

    def handle_event(self, event: pygame.event.Event):
        if self.active_dialog:
            self.active_dialog.handle_event(event)
            return

        action = self.turn_controls.handle_event(event)
        if action == 'roll':
            self._do_dice_roll()
            return
        if action == 'next_phase':
            self._do_next_phase()
            return
        if action == 'end_turn':
            self._do_end_turn()
            return

        self.tabletop.handle_event(event)

        if self._can_trade():
            if self.btn_bank.handle_event(event):
                self._open_bank_dialog()
                return
            if self.btn_trade.handle_event(event):
                self._open_player_dialog()
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._can_build():
                self._handle_click(event.pos)

    def _can_trade(self):
        if self.turn_manager.is_setup_phase:
            return False
        return self.turn_manager.current_phase == TurnPhase.COMMERCE

    def _can_build(self):
        if self.turn_manager.is_setup_phase:
            return True
        return self.turn_manager.current_phase == TurnPhase.CONSTRUCTION

    def _do_dice_roll(self):
        self.turn_manager.roll_dice()
        self.tabletop.distribute_resources_for_roll(self.turn_manager.dice_sum)
        self._update_turn_state()

    def _do_next_phase(self):
        self.turn_manager.next_phase()
        self._update_turn_state()

    def _do_end_turn(self):
        self.turn_manager.next_phase()
        self._update_turn_state()

    def _update_turn_state(self):
        self.player_list.set_current_player(self.current_player)
        setup_needs_house = self.turn_manager.is_setup_phase and not self.turn_manager.setup_built_house
        setup_needs_road = self.turn_manager.is_setup_phase and not self.turn_manager.setup_built_road
        self.turn_controls.set_state(
            self.turn_manager.current_phase,
            self.turn_manager.last_dice_roll,
            self.turn_manager.is_setup_phase,
            setup_needs_house,
            setup_needs_road
        )
        self.resource_display.set_player(self.current_player)
        can_trade = self._can_trade()
        self.btn_bank.enabled = can_trade
        self.btn_trade.enabled = can_trade

    def _handle_click(self, pos):
        from components.house import House
        from components.road import Road
        target = self.tabletop.get_buildable_at(pos)
        if target:
            was_empty = isinstance(target, House) and target.level == 0
            # Passa all_roads se for uma estrada
            if isinstance(target, Road):
                result = target.try_build(self.current_player, self.tabletop.roads)
            else:
                result = target.try_build(self.current_player)
            
            if result:
                if was_empty and target.level == 1:
                    self._on_settlement_placed(self.current_player, target)
                if self.turn_manager.is_setup_phase:
                    if isinstance(target, House):
                        self.turn_manager.setup_record_house()
                    elif isinstance(target, Road):
                        self.turn_manager.setup_record_road()
                    if self.turn_manager.setup_turn_complete():
                        self.turn_manager.next_turn()
                self._update_turn_state()

    # ---------- Todo o código de Dialogs da development foi mantido ----------
    def _open_bank_dialog(self):
        self.active_dialog = BankTradeDialog(
            self.current_player,
            self.tabletop.ports,
            on_confirm=self._execute_bank_trade,
            on_cancel=self._close_dialog
        )
        self.active_dialog.show()

    def _execute_bank_trade(self, give_type, give_count, receive_type):
        BankTrade.execute(self.current_player, give_type, give_count, receive_type)
        self._close_dialog()

    def _open_player_dialog(self):
        self.active_dialog = PlayerTradeDialog(
            self.current_player,
            self.players,
            on_propose=self._show_offer_dialog,
            on_cancel=self._close_dialog
        )
        self.active_dialog.show()

    def _show_offer_dialog(self, offer):
        self.pending_offer = offer
        self.pending_targets = [p for p in self.players if p != offer.proposer]
        self._show_next_target()

    def _show_next_target(self):
        if not self.pending_targets:
            self.pending_offer = None
            self._close_dialog()
            return
        target = self.pending_targets.pop(0)
        self.active_dialog = TradeOfferDialog(
            self.pending_offer,
            target,
            on_accept=self._execute_player_trade,
            on_reject=self._show_next_target
        )
        self.active_dialog.show()

    def _execute_player_trade(self, offer, acceptor):
        offer.target = acceptor
        PlayerTrade.execute(offer)
        self.pending_offer = None
        self.pending_targets = []
        self._close_dialog()

    def _close_dialog(self):
        self.active_dialog = None

    def update(self, dt: float):
        self.tabletop.update(dt)
        self.btn_bank.update()
        self.btn_trade.update()
        self.turn_controls.update()

    def render(self, surface: pygame.Surface):
        surface.fill(SEA_BLUE)
        self.tabletop.render(surface)

        self.resource_display.render(surface)
        self.btn_bank.render(surface)
        self.btn_trade.render(surface)
        self.player_list.render(surface)
        self.turn_controls.render(surface)

        if self.active_dialog:
            self.active_dialog.render(surface)

    def _on_settlement_placed(self, player, house):
        if player.settlements_count == 2:
            self.tabletop.distribute_initial_resources(player, house)
