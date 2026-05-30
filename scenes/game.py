import pygame
from .base_scene import BaseScene
from models.player import Player
from core.turn_manager import TurnManager
from components.tabletop import Tabletop
from components.button import Button
from components.resource_display import ResourceDisplay
from components.development_display import DevelopmentDisplay
from components.bank_trade_dialog import BankTradeDialog
from components.player_trade_dialog import PlayerTradeDialog, TradeOfferDialog
from components.player_list_panel import PlayerListPanel
from components.turn_controls import TurnControls
from core.trade import BankTrade, PlayerTrade
from systems.card_manager import CardManager
from ui.toast import ToastManager
from constants.types import ROCK, LAMB, WHEAT, TREE, BRICK
from components.base_card import (
    ChapelCard,
    KnightCard,
    LibraryCard,
    MarketCard,
    PalaceCard,
    RoadBuildingCard,
    UniversityCard,
    YearOfPlentyCard,
    MonopolyCard,
    VictoryPointCard,
)
from components.card_states import CardState
from constants.colors import RED, BLUE, GREEN, BLACK, YELLOW, SEA_BLUE
from constants.phases import TurnPhase
from constants.victory_points import CHAPEL, LIBRARY, MARKET
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.sound import SoundManager
from models.bank import Bank
from components.year_of_plenty_dialog import YearOfPlentyDialog
from components.monopoly_dialog import MonopolyDialog
from components.road_building_dialog import RoadBuildingDialog


class Game(BaseScene):
    def __init__(self, manager=None):
        self.manager = manager
        self.players = [
            Player(1, "Player 1", RED),
            Player(2, "Player 2", BLUE),
            Player(3, "Player 3", GREEN),
            Player(4, "Player 4", YELLOW)
        ]

        """ # Para teste: dar cartas aos jogadores
        self.players[0].victory_point_cards.append(CHAPEL)
        self.players[1].victory_point_cards.extend([LIBRARY, MARKET]) """

        self.turn_manager = TurnManager(self.players)
        self.card_manager = CardManager(self.players)
        self.turn_manager.shuffle_player_order()

        hex_radius = int(SCREEN_HEIGHT * 0.085)
        board_x = int(SCREEN_WIDTH * 0.2)
        board_y = int(SCREEN_HEIGHT * 0.15)
        self.tabletop = Tabletop(board_x, board_y, hex_radius)

        self._setup_ui()
        self.toast_manager = ToastManager()
        self.active_dialog = None
        # bank for Year of Plenty and other interactions
        self.bank = Bank()
        self.pending_offer = None
        self.pending_targets = []
        self._update_turn_state()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self._last_player = self.current_player

    @property
    def current_player(self):
        return self.turn_manager.current_player

    def _setup_ui(self):
        scale = SCREEN_HEIGHT / 600.0
        margin = int(SCREEN_WIDTH * 0.02)
        bottom_margin = int(SCREEN_HEIGHT * 0.15)

        self.resource_display = ResourceDisplay(SCREEN_WIDTH * 0.2, SCREEN_HEIGHT - bottom_margin, scale)
        self.resource_display.set_player(self.current_player)

        # Development HUD (hidden by default) and toggle button
        self.development_display = DevelopmentDisplay(self.resource_display.x, self.resource_display.y, scale)
        self.show_development_cards = False

        btn_w = int(88 * scale)
        btn_h = int(33 * scale)
        btn_font = int(15 * scale)
        btn_x = int(SCREEN_WIDTH * 0.45)
        btn_y = SCREEN_HEIGHT - bottom_margin - 10
        btn_gap = int(10 * scale)
        self.btn_bank = Button(btn_x, btn_y, btn_w, btn_h, "Banco", font_size=btn_font)
        self.btn_trade = Button(btn_x + btn_w + btn_gap, btn_y, btn_w, btn_h, "Trocar", font_size=btn_font)
        # Toggle button replaces the old "Ver Cartas" button
        dev_btn_w = btn_w
        # use same width as other buttons to avoid overlap
        self.btn_dev_cards = Button(btn_x, btn_y + btn_h + btn_gap, dev_btn_w, btn_h, "Desenv.", font_size=btn_font)
        self.btn_buy_card = Button(btn_x + btn_w + btn_gap, btn_y + btn_h + btn_gap, btn_w, btn_h, "Comprar Carta", font_size=btn_font)


        panel_width = int(240 * scale)
        panel_width = max(200, min(panel_width, 350))
        self.player_list = PlayerListPanel(SCREEN_WIDTH - panel_width - margin, margin, panel_width, self.players, scale)

        turn_ctrl_height = int(190 * scale)
        self.turn_controls = TurnControls(SCREEN_WIDTH - panel_width - margin, SCREEN_HEIGHT - turn_ctrl_height - margin, panel_width, scale)

    def handle_event(self, event: pygame.event.Event):
        if self.active_dialog:
            if self.active_dialog.handle_event(event):
                # Se o diálogo manipulou o evento, não fazemos mais nada
                return
            # Se o diálogo não manipulou (pode ter sido fechado), limpamos
            if not self.active_dialog.visible:
                 self._close_dialog()
            return

        # Debug hotkey: press D to give current player resources (useful for testing)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
            p = self.current_player
            p.inventory.add(ROCK, 1)
            p.inventory.add(LAMB, 1)
            p.inventory.add(WHEAT, 1)
            self.toast_manager.show(f"Recursos adicionados a {p.name}")
            self._update_turn_state()
            return

        # legacy hand/dropdown removed: HUD is the single source-of-truth

        # If the development HUD is visible, allow clicking cards
        if getattr(self, "show_development_cards", False):
            res = self.development_display.handle_event(event)
            card = None
            msg = None
            if isinstance(res, tuple):
                card, msg = res
            else:
                card = res

            if card:
                # start play flow for this development card
                self._play_development_card(card)
                return
            if msg:
                # show a toast at the top of the screen explaining why
                self.toast_manager.show(msg)
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


        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.pop()
                return

        if self._can_build() or self._can_trade():
            if self.btn_dev_cards.handle_event(event):
                # Toggle between resource HUD and development HUD
                self.show_development_cards = not getattr(self, "show_development_cards", False)
                if self.show_development_cards:
                    self.development_display.set_player(self.current_player)
                else:
                    self.resource_display.set_player(self.current_player)
                self._update_turn_state()
                return
            # Buying development cards is only allowed outside setup phase
            if self._can_build() and not self.turn_manager.is_setup_phase and self.btn_buy_card.handle_event(event):
                success = self.card_manager.attempt_buy_card(self.current_player)
                if success:
                    SoundManager().play('construction')
                    # Ensure the development HUD references the current player so
                    # the newly purchased (LOCKED) card is reflected immediately
                    self.development_display.set_player(self.current_player)
                    self.toast_manager.show("Carta comprada")
                    self._update_turn_state()
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
        SoundManager().play('dice_roll')
        self.turn_manager.roll_dice()
        self.tabletop.distribute_resources_for_roll(self.turn_manager.dice_sum)
        SoundManager().play('draw_card')
        self._update_turn_state()

    def _do_next_phase(self):
        self.turn_manager.next_phase()
        self._update_turn_state()

    def _do_end_turn(self):
        self.turn_manager.next_phase()
        self._update_turn_state()

    def _update_turn_state(self):
        if not hasattr(self, '_last_player') or self._last_player != self.current_player:
            self.card_manager.on_turn_start(self.current_player)
            self._last_player = self.current_player

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
        self.btn_dev_cards.enabled = can_trade or self._can_build()
        # Buying development cards is disabled during setup phase
        self.btn_buy_card.enabled = self._can_build() and not self.turn_manager.is_setup_phase
        # Update toggle button text (repurposed `btn_dev_cards`)
        if getattr(self, "show_development_cards", False):
            # shorter label shown when HUD is in development mode
            self.btn_dev_cards.text = "Recursos"
            self.development_display.set_player(self.current_player)
        else:
            self.btn_dev_cards.text = "Desenv."
            self.resource_display.set_player(self.current_player)

    def _handle_click(self, pos):
        from components.house import House
        from components.road import Road
        target = self.tabletop.get_buildable_at(pos)
        if target:
            # RN26: Durante setup, limitar 1 casa e 1 estrada por turno
            if self.turn_manager.is_setup_phase:
                if isinstance(target, House) and self.turn_manager.setup_built_house:
                    target._invalid_timer = 0.4  # Mostrar indicador visual
                    SoundManager().play('invalid_action')
                    return  # Já construiu uma casa neste turno de setup
                if isinstance(target, Road) and self.turn_manager.setup_built_road:
                    target._invalid_timer = 0.4  # Mostrar indicador visual
                    SoundManager().play('invalid_action')
                    return  # Já construiu uma estrada neste turno de setup
            
            was_empty = isinstance(target, House) and target.level == 0
            # Passa all_roads se for uma estrada
            if isinstance(target, Road):
                result = target.try_build(self.current_player, self.tabletop.roads)
            else:
                result = target.try_build(self.current_player)
            
            if result:
                if was_empty and target.level == 1:
                    SoundManager().play('construction')
                    self._on_settlement_placed(self.current_player, target)
                if self.turn_manager.is_setup_phase:
                    if isinstance(target, House):
                        SoundManager().play('construction')
                        self.turn_manager.setup_record_house()
                    elif isinstance(target, Road):
                        SoundManager().play('road')
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

    # --- Development card play orchestrator ---
    def _play_development_card(self, card):
        """Start interactive flow for the given development `card`."""
        self._pending_card = card
        owner = self.current_player
        can, reason = card.can_activate(owner.played_development_card_this_turn)
        if not can:
            self.toast_manager.show(reason)
            return

        if isinstance(card, YearOfPlentyCard):
            self.active_dialog = YearOfPlentyDialog(owner, self.bank, on_confirm=self._resolve_year_of_plenty, on_cancel=self._close_dialog)
            self.active_dialog.show()
            return

        if isinstance(card, MonopolyCard):
            # Monopoly dialog: do not darken the entire board (no full-screen overlay)
            self.active_dialog = MonopolyDialog(owner, on_confirm=self._resolve_monopoly, on_cancel=self._close_dialog, overlay_fullscreen=False)
            self.active_dialog.show()
            return

        if isinstance(card, RoadBuildingCard):
            self.active_dialog = RoadBuildingDialog(owner, self.tabletop, on_confirm=self._resolve_road_building, on_cancel=self._close_dialog)
            self.active_dialog.show()
            return
        
        if (isinstance(card, UniversityCard) or isinstance(card, LibraryCard) or isinstance(card, MarketCard) or isinstance(card, PalaceCard) or isinstance(card, ChapelCard) or isinstance(card, VictoryPointCard)):
            self.current_player.use_victory_card()
            self.card_manager.attempt_activate_card(owner, card)
            self.toast_manager.show("Carta de Ponto de Vitória revelada!")
            SoundManager().play('construction')
            return

        # Fallback: immediate activation for other cards
        success = self.card_manager.attempt_activate_card(owner, card)
        if success:
            SoundManager().play('construction')
            self.toast_manager.show("Carta ativada")
            self._update_turn_state()
        else:
            self.toast_manager.show("Não foi possível ativar a carta")

    def _resolve_year_of_plenty(self, resources):
        card = getattr(self, '_pending_card', None)
        if card is None:
            return
        success = self.card_manager.attempt_activate_card(self.current_player, card, resources=resources, bank=self.bank)
        if success:
            self.toast_manager.show(f"Recebeu recursos: {len(resources)}")
            SoundManager().play('construction')
        else:
            self.toast_manager.show("Falha ao resolver Ano de Fartura")
        self._close_dialog()
        self._update_turn_state()

    def _resolve_monopoly(self, resource):
        card = getattr(self, '_pending_card', None)
        if card is None:
            return
        # Accept both numeric ids and string names for convenience
        if isinstance(resource, str):
            key = resource.strip().lower()
            name_map = {
                'rock': ROCK, 'ore': ROCK,
                'wood': TREE, 'lumber': TREE,
                'wheat': WHEAT, 'grain': WHEAT,
                'sheep': LAMB, 'wool': LAMB,
                'brick': BRICK,
            }
            resource_id = name_map.get(key, None)
            if resource_id is None:
                self.toast_manager.show("Recurso inválido para Monopólio")
                self._close_dialog()
                return
        else:
            resource_id = resource

        # compute expected collected amount for feedback
        total = sum(p.inventory.get_count(resource_id) for p in self.players if p != self.current_player)
        success = self.card_manager.attempt_activate_card(self.current_player, card, resource=resource_id)
        if success:
            self.toast_manager.show(f"Monopolizou {total} unidades")
            SoundManager().play('construction')
        else:
            self.toast_manager.show("Falha ao resolver Monopólio")
        self._close_dialog()
        self._update_turn_state()

    def _resolve_road_building(self, edges):
        card = getattr(self, '_pending_card', None)
        if card is None:
            return
        success = self.card_manager.attempt_activate_card(self.current_player, card, tabletop=self.tabletop, edges=edges)
        if success:
            self.toast_manager.show("Estradas construídas")
            SoundManager().play('road')
        else:
            self.toast_manager.show("Falha ao construir estradas")
        self._close_dialog()
        self._update_turn_state()

    def _execute_player_trade(self, offer, acceptor):
        offer.target = acceptor
        if PlayerTrade.execute(offer):
            SoundManager().play('confirm_trade')
        self.pending_offer = None
        self.pending_targets = []
        self._close_dialog()

    def _close_dialog(self):
        self.active_dialog = None

    def update(self, dt: float):
        self.tabletop.update(dt)
        # Update both displays so hover and internal state stay in sync
        try:
            self.resource_display.update(dt)
        except Exception:
            pass
        try:
            self.development_display.update(dt)
        except Exception:
            pass

        self.btn_bank.update()
        self.btn_trade.update()
        self.turn_controls.update()
        self.btn_dev_cards.update()
        self.btn_buy_card.update()
        # legacy hand/dropdown removed: nothing to update here
        self.toast_manager.update(dt)

        self.turn_manager.turn_time_elapsed += dt
        time_left = max(0.0, 90.0 - self.turn_manager.turn_time_elapsed)

        self.turn_controls.set_timer(time_left)

        if time_left <= 0:
            self._force_skip_turn()

    def _force_skip_turn(self):
        if self.active_dialog:
            self._close_dialog()

        SoundManager().play('invalid_action')

        self.turn_manager.next_turn()
        self._update_turn_state()

    def render(self, surface: pygame.Surface):
        surface.fill(SEA_BLUE)
        self.tabletop.render(surface)
        # HUD overlay area: render either resources or development cards in the same space
        if getattr(self, "show_development_cards", False):
            self.development_display.render(surface)
        else:
            self.resource_display.render(surface)

        self.btn_bank.render(surface)
        self.btn_trade.render(surface)
        self.player_list.render(surface)
        self.turn_controls.render(surface)
        self.btn_dev_cards.render(surface)
        self.btn_buy_card.render(surface)

        if self.active_dialog:
            self.active_dialog.render(surface)

        # legacy hand/dropdown removed: HUD modal eliminated

        # Toasts on top
        self.toast_manager.render(surface)

    def _on_settlement_placed(self, player, house):
        if player.settlements_count == 2:
            self.tabletop.distribute_initial_resources(player, house)

