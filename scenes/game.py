import random
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
from components.development_card_display import DevelopmentCardDisplay
from components.development_card_dialog import DevelopmentCardDialog
from core.trade import BankTrade, PlayerTrade
from systems.card_manager import CardManager
from ui.toast import ToastManager
from constants.types import ROCK, LAMB, WHEAT, TREE, BRICK
from components.base_card import (
    KnightCard,
    RoadBuildingCard,
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
from components.robber_dialogs import DiscardResourcesDialog, RobberStealDialog, RESOURCE_NAMES


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
        self.awaiting_robber_tile = False
        self._discard_queue = []
        self._discarding_player = None
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

        btn_w = int(88 * scale)
        btn_h = int(33 * scale)
        btn_font = int(15 * scale)
        btn_x = int(SCREEN_WIDTH * 0.45)
        btn_y = SCREEN_HEIGHT - bottom_margin - 10
        btn_gap = int(10 * scale)
        self.btn_bank = Button(btn_x, btn_y, btn_w, btn_h, "Banco", font_size=btn_font)
        self.btn_trade = Button(btn_x + btn_w + btn_gap, btn_y, btn_w, btn_h, "Trocar", font_size=btn_font)
        self.btn_buy_card = Button(btn_x, btn_y + btn_h + btn_gap, btn_w, btn_h, "Comprar Carta", font_size=btn_font)


        panel_width = int(240 * scale)
        panel_width = max(200, min(panel_width, 350))
        self.player_list = PlayerListPanel(SCREEN_WIDTH - panel_width - margin, margin, panel_width, self.players, scale)

        turn_ctrl_height = int(190 * scale)
        self.turn_controls = TurnControls(SCREEN_WIDTH - panel_width - margin, SCREEN_HEIGHT - turn_ctrl_height - margin, panel_width, scale)

        card_display_x = int(SCREEN_WIDTH * 0.65)
        card_display_y = SCREEN_HEIGHT - bottom_margin - 10
        self.card_display = DevelopmentCardDisplay(card_display_x, card_display_y, scale, on_click=self._open_dev_card_dialog)

    def handle_event(self, event: pygame.event.Event):
        if self.active_dialog:
            if self.active_dialog.handle_event(event):
                # Se o diálogo manipulou o evento, não fazemos mais nada
                return
            # Se o diálogo não manipulou (pode ter sido fechado), limpamos
            if not self.active_dialog.visible:
                 self._close_dialog()
            return

        if self.awaiting_robber_tile:
            self.tabletop.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_robber_tile_click(event.pos)
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

        if self.card_display.handle_event(event):
            return

        if self._can_build() and not self.turn_manager.is_setup_phase and self.btn_buy_card.handle_event(event):
            success = self.card_manager.attempt_buy_card(self.current_player)
            if success:
                SoundManager().play('construction')
                self.toast_manager.show("Carta comprada")
                self._update_turn_state()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.pop()
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
        self._update_turn_state()

        if self.turn_manager.dice_sum == 7:
            self._start_seven_robber_flow()
            return

        self.tabletop.distribute_resources_for_roll(self.turn_manager.dice_sum)
        SoundManager().play('draw_card')
        self._update_turn_state()

    def _start_seven_robber_flow(self):
        self.toast_manager.show("Saiu 7: o ladrao deve ser movido")
        self._discard_queue = [
            (player, player.inventory.total() // 2)
            for player in self.players
            if player.inventory.total() > 7
        ]
        self._open_next_discard_dialog()

    def _open_next_discard_dialog(self):
        if not self._discard_queue:
            self._discarding_player = None
            self._begin_robber_tile_selection()
            return

        player, discard_count = self._discard_queue.pop(0)
        self._discarding_player = player
        self.active_dialog = DiscardResourcesDialog(player, discard_count, on_confirm=self._confirm_discard)
        self.active_dialog.show()

    def _confirm_discard(self, selection):
        player = self._discarding_player
        if player is None:
            return

        for resource, count in selection.items():
            player.inventory.remove(resource, count)

        self.active_dialog = None
        self.toast_manager.show(f"{player.name} descartou {sum(selection.values())} recurso(s)")
        self._update_turn_state()
        self._open_next_discard_dialog()

    def _begin_robber_tile_selection(self):
        self.awaiting_robber_tile = True
        self.toast_manager.show("Escolha outro terreno para mover o ladrao")

    def _handle_robber_tile_click(self, pos):
        tile = self.tabletop.get_tile_at(pos)
        if tile is None:
            return
        if tile is self.tabletop.robber_tile:
            self.toast_manager.show("O ladrao precisa ir para outro terreno")
            return

        if not self.tabletop.move_robber(tile):
            return

        self.awaiting_robber_tile = False
        SoundManager().play('ladrao_move')
        self._finish_robber_move(tile)

    def _finish_robber_move(self, tile):
        candidates = self._robber_steal_candidates(tile)
        if not candidates:
            self.toast_manager.show("Ladrao movido. Nao ha jogador adjacente para roubar")
            self._update_turn_state()
            return

        self.active_dialog = RobberStealDialog(
            candidates,
            on_select=self._steal_random_resource,
            on_skip=self._skip_robber_steal
        )
        self.active_dialog.show()

    def _robber_steal_candidates(self, tile):
        candidates = []
        for house in tile.extract_houses():
            if not house or not house.owner or house.level <= 0:
                continue
            owner = house.owner
            if owner is self.current_player or owner.inventory.total() <= 0:
                continue
            if owner not in candidates:
                candidates.append(owner)

        return [player for player in self.players if player in candidates]

    def _steal_random_resource(self, victim):
        resource_pool = []
        for resource, count in victim.inventory.cards.items():
            resource_pool.extend([resource] * count)

        if not resource_pool:
            self.toast_manager.show(f"{victim.name} nao tem recursos para roubar")
            self._skip_robber_steal()
            return

        resource = random.choice(resource_pool)
        victim.inventory.remove(resource, 1)
        self.current_player.inventory.add(resource, 1)
        self.active_dialog = None
        resource_name = RESOURCE_NAMES.get(resource, "recurso")
        self.toast_manager.show(f"{self.current_player.name} roubou {resource_name} de {victim.name}")
        SoundManager().play('draw_card')
        self._update_turn_state()

    def _skip_robber_steal(self):
        self.active_dialog = None
        self.toast_manager.show("Ladrao movido")
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
        self.card_display.enabled = not self.turn_manager.is_setup_phase
        self.btn_buy_card.enabled = self._can_build() and not self.turn_manager.is_setup_phase

        winner = self.turn_manager.check_victory()
        if winner:
            self._show_victory_screen(winner)

    def _show_victory_screen(self, winner):
        self.toast_manager.show(f"{winner.name} venceu com {winner.victory_points} pontos!")
        SoundManager().play('construction')
        from components.modal import Modal
        from components.button import Button

        class VictoryDialog(Modal):
            def __init__(dialog_self, player, on_close):
                width = int(SCREEN_WIDTH * 0.4)
                height = int(SCREEN_HEIGHT * 0.3)
                super().__init__(width, height, "Fim de Jogo!")
                dialog_self.player = player
                dialog_self.on_close = on_close
                btn_w, btn_h = 120, 40
                btn_x = dialog_self.x + (dialog_self.width - btn_w) // 2
                btn_y = dialog_self.y + dialog_self.height - btn_h - 20
                dialog_self.btn_close = Button(btn_x, btn_y, btn_w, btn_h, "Menu Principal", on_click=on_close)
                try:
                    dialog_self.font = pygame.font.Font("./assets/fonts/MedievalSharp-Regular.ttf", 24)
                except Exception:
                    dialog_self.font = pygame.font.SysFont("Arial", 24)

            def handle_event(dialog_self, event):
                if not dialog_self.visible:
                    return False
                if dialog_self.btn_close.handle_event(event):
                    return True
                return super().handle_event(event)

            def render(dialog_self, surface):
                if not dialog_self.visible:
                    return
                super().render(surface)
                text = f"{dialog_self.player.name} venceu!"
                text_surf = dialog_self.font.render(text, True, (50, 50, 50))
                text_rect = text_surf.get_rect(centerx=dialog_self.rect.centerx, top=dialog_self.y + 60)
                surface.blit(text_surf, text_rect)
                pts_text = f"{dialog_self.player.victory_points} pontos de vitória"
                pts_surf = dialog_self.font.render(pts_text, True, (80, 80, 80))
                pts_rect = pts_surf.get_rect(centerx=dialog_self.rect.centerx, top=text_rect.bottom + 10)
                surface.blit(pts_surf, pts_rect)
                dialog_self.btn_close.render(surface)

        def go_to_menu():
            self._close_dialog()
            self.manager.pop()

        self.active_dialog = VictoryDialog(winner, go_to_menu)
        self.active_dialog.show()

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
        if self.active_dialog:
            self.active_dialog.update(dt)
        try:
            self.resource_display.update(dt)
        except Exception:
            pass

        self.btn_bank.update()
        self.btn_trade.update()
        self.turn_controls.update()
        self.card_display.update()
        self.btn_buy_card.update()
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
        self.resource_display.render(surface)

        self.btn_bank.render(surface)
        self.btn_trade.render(surface)
        self.player_list.render(surface)
        self.turn_controls.render(surface)
        self.card_display.render(surface)
        self.btn_buy_card.render(surface)

        if self.active_dialog:
            self.active_dialog.render(surface)

        # legacy hand/dropdown removed: HUD modal eliminated

        # Toasts on top
        self.toast_manager.render(surface)

    def _on_settlement_placed(self, player, house):
        if player.settlements_count == 2:
            self.tabletop.distribute_initial_resources(player, house)

    def _open_dev_card_dialog(self):
        self.active_dialog = DevelopmentCardDialog(
            self.current_player,
            on_cancel=self._close_dialog,
            on_play_card=self._on_dialog_play_card
        )
        self.active_dialog.show()

    def _on_dialog_play_card(self, card):
        self._close_dialog()
        self._play_development_card(card)
