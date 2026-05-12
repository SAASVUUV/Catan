import pygame
from .base_scene import BaseScene
from models.player import Player
from components.tabletop import Tabletop
from components.button import Button
from components.resource_display import ResourceDisplay
from components.bank_trade_dialog import BankTradeDialog
from components.player_trade_dialog import PlayerTradeDialog, TradeOfferDialog
from core.trade import BankTrade, PlayerTrade
from constants.colors import RED, BLUE, GREEN, BLACK, YELLOW, SEA_BLUE
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
        self.turn_index = 0
        self.tabletop = Tabletop(100, 100, 50)
        self._setup_ui()
        self.active_dialog = None
        self.pending_offer = None
        self.pending_targets = []
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    @property
    def current_player(self):
        return self.players[self.turn_index]

    def _setup_ui(self):
        self.resource_display = ResourceDisplay(50, SCREEN_HEIGHT - 85)
        self.resource_display.set_player(self.current_player)

        btn_x = 320
        btn_y = SCREEN_HEIGHT - 95
        self.btn_bank = Button(btn_x, btn_y, 100, 35, "Banco", font_size=16)
        self.btn_trade = Button(btn_x, btn_y + 40, 100, 35, "Trocar", font_size=16)

    def handle_event(self, event: pygame.event.Event):
        if self.active_dialog:
            self.active_dialog.handle_event(event)
            return

        self.tabletop.handle_event(event)

        if self.btn_bank.handle_event(event):
            self._open_bank_dialog()
            return

        if self.btn_trade.handle_event(event):
            self._open_player_dialog()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)

    def _handle_click(self, pos):
        from components.house import House
        target = self.tabletop.get_buildable_at(pos)
        if target:
            was_empty = isinstance(target, House) and target.level == 0
            if target.try_build(self.current_player):
                if was_empty and target.level == 1:
                    self._on_settlement_placed(self.current_player, target)

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

    def render(self, surface: pygame.Surface):
        surface.fill(SEA_BLUE)
        self.tabletop.render(surface)

        self.resource_display.render(surface)
        self.btn_bank.render(surface)
        self.btn_trade.render(surface)

        if self.active_dialog:
            self.active_dialog.render(surface)

    def _on_settlement_placed(self, player, house):
        """RN18: Distribui recursos automaticamente na segunda aldeia do setup."""
        if player.settlements_count == 2:
            self.tabletop.distribute_initial_resources(player, house)
