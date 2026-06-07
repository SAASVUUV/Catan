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
from core.trade import BankTrade, PlayerTrade, TradeOffer
from systems.card_manager import CardManager
from systems.achievements import AchievementsManager
from systems.bot_ai import BotDecisionMaker
from ui.toast import ToastManager
from constants.types import ROCK, LAMB, WHEAT, TREE, BRICK, GENERIC
from components.base_card import (
    KnightCard,
    RoadBuildingCard,
    YearOfPlentyCard,
    MonopolyCard,
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
    def __init__(self, manager=None, bot_list=None):
        self.manager = manager
        self.players = [
            Player(1, "Player 1", RED),
            Player(2, "Player 2", BLUE),
            Player(3, "Player 3", GREEN),
            Player(4, "Player 4", YELLOW)
        ]
        if bot_list:
            for slot in bot_list:
                if 1 <= slot <= 4:
                    self.players[slot - 1].is_bot = True
        print(bot_list)

        """ # Para teste: dar cartas aos jogadores
        self.players[0].victory_point_cards.append(CHAPEL)
        self.players[1].victory_point_cards.extend([LIBRARY, MARKET]) """

        self.turn_manager = TurnManager(self.players)
        self.card_manager = CardManager(self.players)
        self.achievements_manager = AchievementsManager(self.players)
        self.turn_manager.shuffle_player_order()
        
        # Initialize bot decision makers
        self.bot_deciders = {}
        for player in self.players:
            if player.is_bot:
                self.bot_deciders[player.id] = BotDecisionMaker(player)

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
        self._bot_timer = 0
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
        second_row_y = btn_y + btn_h + btn_gap
        self.btn_dev_cards = Button(btn_x, second_row_y, btn_w, btn_h, "Desenv.", font_size=btn_font)
        self.btn_buy_card = Button(btn_x + btn_w + btn_gap, second_row_y, btn_w, btn_h, "Comprar Carta", font_size=btn_font)


        panel_width = int(290 * scale)
        panel_width = max(250, min(panel_width, 400))
        self.player_list = PlayerListPanel(SCREEN_WIDTH - panel_width - margin, margin, panel_width, self.players, scale)

        turn_ctrl_height = int(190 * scale)
        turn_ctrl_y = SCREEN_HEIGHT - turn_ctrl_height - margin
        self.turn_controls = TurnControls(SCREEN_WIDTH - panel_width - margin, turn_ctrl_y, panel_width, scale)

        from components.development_display import DevelopmentDisplay
        self.development_display = DevelopmentDisplay(SCREEN_WIDTH * 0.2, SCREEN_HEIGHT - bottom_margin, scale)
        self.show_development_cards = False

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

        if self.show_development_cards:
            result = self.development_display.handle_event(event)
            if result is not None:
                if isinstance(result, tuple):
                    self.toast_manager.show(result[1])
                else:
                    self._play_development_card(result)
                return

        if self._can_build() and not self.turn_manager.is_setup_phase and self.btn_buy_card.handle_event(event):
            success = self.card_manager.attempt_buy_card(self.current_player)
            if success:
                SoundManager().play('construction')
                self.development_display.set_player(self.current_player)
                self.toast_manager.show("Carta comprada")
                self._update_turn_state()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.pop()
                return

        if self._can_build() or self._can_trade():
            if self.btn_dev_cards.handle_event(event):
                self.show_development_cards = not self.show_development_cards
                if self.show_development_cards:
                    self.development_display.set_player(self.current_player)
                else:
                    self.resource_display.set_player(self.current_player)
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
        
        # If bot, automatically discard
        if player.is_bot:
            bot = self.bot_deciders.get(player.id)
            if bot:
                selection = bot.select_discard_resources(discard_count)
                self._confirm_discard(selection)
                return
        
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
        
        # If current player is bot, automatically move robber
        player = self.current_player
        if player.is_bot:
            bot = self.bot_deciders.get(player.id)
            if bot:
                all_tiles = self.tabletop.tiles
                available_tiles = [t for t in all_tiles if t != self.tabletop.robber_tile]
                if available_tiles:
                    best_tile = bot.select_robber_tile(available_tiles)
                    if best_tile:
                        self.tabletop.move_robber(best_tile)
                        self.awaiting_robber_tile = False
                        SoundManager().play('ladrao_move')
                        self._finish_robber_move(best_tile)

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
        
        if self.current_player.is_bot:
            victim = random.choice(candidates)
            self._steal_random_resource(victim)
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
        self.btn_dev_cards.enabled = can_trade or self._can_build()
        self.btn_buy_card.enabled = self._can_build() and not self.turn_manager.is_setup_phase
        if self.show_development_cards:
            self.btn_dev_cards.text = "Recursos"
            self.development_display.set_player(self.current_player)
        else:
            self.btn_dev_cards.text = "Desenv."
            self.resource_display.set_player(self.current_player)

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
                result = target.try_build(self.current_player, all_roads=self.tabletop.roads)
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
                if isinstance(target, Road):
                    SoundManager().play('road')
                    self.achievements_manager.update_longest_road(self.tabletop.roads)
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
        
        # If target is a bot, automatically accept or reject
        if target.is_bot:
            bot = self.bot_deciders.get(target.id)
            if bot and bot.should_accept_trade_offer(self.pending_offer):
                self._execute_player_trade(self.pending_offer, target)
                self._show_next_target()
            else:
                self._show_next_target()
            return
        
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

        if isinstance(card, KnightCard):
            self.card_manager.attempt_activate_card(owner, card)
            owner.knights_played += 1
            self.achievements_manager.update_largest_army()
            self._begin_robber_tile_selection()
            self.toast_manager.show("Escolha um terreno para mover o ladrão")
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
            self.achievements_manager.update_longest_road(self.tabletop.roads)
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
        if self.show_development_cards:
            self.development_display.update()
        else:
            try:
                self.resource_display.update(dt)
            except Exception:
                pass

        self.btn_bank.update()
        self.btn_trade.update()
        self.turn_controls.update()
        self.btn_dev_cards.update()
        self.btn_buy_card.update()
        self.toast_manager.update(dt)

        self.turn_manager.turn_time_elapsed += dt
        time_left = max(0.0, 90.0 - self.turn_manager.turn_time_elapsed)

        self.turn_controls.set_timer(time_left)

        if time_left <= 0:
            self._force_skip_turn()
        
        # Execute bot actions
        if self.current_player.is_bot and not self.active_dialog and not self.awaiting_robber_tile:
            self._bot_timer += dt
            if self._bot_timer >= 1.0:  # Execute bot action every 1 second
                self._bot_timer = 0.0
                self._execute_bot_action()


    def _force_skip_turn(self):
        if self.active_dialog:
            self._close_dialog()

        SoundManager().play('invalid_action')

        self.turn_manager.next_turn()
        self._update_turn_state()

    def render(self, surface: pygame.Surface):
        surface.fill(SEA_BLUE)
        self.tabletop.render(surface)
        if self.show_development_cards:
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

    # ========== BOT AUTOMATION ==========

    def _execute_bot_action(self):
        """Execute a single bot action based on current game phase."""
        player = self.current_player
        if not player.is_bot:
            return
        
        # Setup phase: auto-place settlement and road
        if self.turn_manager.is_setup_phase:
            self._bot_setup_phase()
            return
        
        # Dice phase: auto-roll
        if self.turn_manager.current_phase == TurnPhase.DICE:
            self._do_dice_roll()
            #self._do_next_phase()
            return
        
        # Commerce phase: auto-trade
        if self.turn_manager.current_phase == TurnPhase.COMMERCE:
            self._bot_commerce_phase()
            return
        
        # Construction phase: auto-build
        if self.turn_manager.current_phase == TurnPhase.CONSTRUCTION:
            self._bot_construction_phase()
            return

    def _bot_setup_phase(self):
        """Bot places settlement and road during setup."""
        if self.turn_manager.setup_turn_complete():
            self.turn_manager.next_turn()
            self._update_turn_state()
            return

        player = self.current_player
        
        # Place settlement if not yet placed
        if not self.turn_manager.setup_built_house:
            buildables = self.tabletop.houses
            houses = [b for b in buildables if hasattr(b, 'level')]
            available = [h for h in houses if h.level == 0 and h._can_place_settlement(player)]
            if available:
                best = random.choice(available[:3])  # Choose random from top 3
                best.try_build(player)
                self.turn_manager.setup_record_house()
                SoundManager().play('construction')
                self._update_turn_state()
                return
        
        # Place road if not yet placed
        if not self.turn_manager.setup_built_road:
            buildables = self.tabletop.roads
            roads = [b for b in buildables if hasattr(b, 'owner') and not hasattr(b, 'level')]
            available = [r for r in roads if not r.owner and r._is_adjacent_to_player(player, self.tabletop.roads)]
            if available:
                best = random.choice(available[:3])
                best.try_build(player, all_roads=self.tabletop.roads)
                self.turn_manager.setup_record_road()
                SoundManager().play('road')
                self._update_turn_state()
                return

    def _bot_commerce_phase(self):
        """Bot handles trading during commerce phase."""
        player = self.current_player
        bot = self.bot_deciders.get(player.id)
        if not bot:
            return
        
        # Try bank trade first
        bank_trade = bot.get_bank_trade(self.tabletop.ports)
        if bank_trade:
            give_type, give_count, receive_type = bank_trade
            BankTrade.execute(player, give_type, give_count, receive_type)
            self.toast_manager.show(f"{player.name} trocou com o banco")
            self._update_turn_state()
            return
        
        # Try 4 for 3 trade with other players
        trade_4_3 = bot.should_make_4_for_3_trade()
        if trade_4_3:
            give_type, give_count, receive_type, receive_count = trade_4_3
            # Create trade offer
            offer = TradeOffer(
                player, 
                None,
                {give_type: give_count},
                {receive_type: receive_count}
            )
            # Find a player who can accept
            for other_player in self.players:
                if other_player == player:
                    continue
                other_player_inventory = other_player.inventory
                if other_player_inventory.has(receive_type, receive_count):
                    # Execute trade
                    other_player_inventory.remove(receive_type, receive_count)
                    other_player_inventory.add(give_type, give_count)
                    player.inventory.remove(give_type, give_count)
                    player.inventory.add(receive_type, receive_count)
                    self.toast_manager.show(f"{player.name} trocou com {other_player.name}")
                    SoundManager().play('confirm_trade')
                    self._update_turn_state()
                    return
                
        if not bank_trade and not trade_4_3:
            # No trades to make, end commerce phase
            self._do_next_phase()

    def _bot_construction_phase(self):
        """Bot handles building during construction phase."""
        player = self.current_player
        bot = self.bot_deciders.get(player.id)
        if not bot:
            return
        
        # Priority: Build settlement
        if bot.should_build_settlement():
            self._bot_build_settlement()
            return
        
        # Priority: Build road
        if bot.should_build_road():
            self._bot_build_road()
            return
        
        # Priority: Build city
        if bot.should_build_city():
            self._bot_build_city()
            return
        
        # Priority: Buy development card
        turn_num = self.turn_manager.turn_count if hasattr(self.turn_manager, 'turn_count') else 0
        if bot.should_buy_development_card(turn_num):
            success = self.card_manager.attempt_buy_card(player)
            if success:
                player.turns_since_last_dev_card = 0
                SoundManager().play('construction')
                self.toast_manager.show(f"{player.name} comprou uma carta de desenvolvimento")
                self._update_turn_state()
                return
        else:
            # Increment dev card purchase counter
            player.turns_since_last_dev_card += 1
        
        # If nothing to do, end turn
        self._do_end_turn()

    def _bot_build_settlement(self):
        """Bot builds a settlement."""
        player = self.current_player
        buildables = self.tabletop.houses
        houses = [b for b in buildables if hasattr(b, 'level')]
        available = [h for h in houses if h.level == 0 and h._can_place_settlement(player)]
        
        if available:
            # Choose random from available
            best = random.choice(available[:5])
            if best.try_build(player):
                SoundManager().play('construction')
                self.toast_manager.show(f"{player.name} construiu uma aldeia")
                self._update_turn_state()
                return True
        return False

    def _bot_build_road(self):
        """Bot builds a road."""
        player = self.current_player
        buildables = self.tabletop.roads
        roads = [b for b in buildables if hasattr(b, 'owner') and not hasattr(b, 'level')]
        available = [r for r in roads if not r.owner and r._is_adjacent_to_player(player, self.tabletop.roads)]
        
        if available:
            # Choose random from available
            best = random.choice(available[:5])
            if best.try_build(player, all_roads=self.tabletop.roads):
                SoundManager().play('road')
                self.toast_manager.show(f"{player.name} construiu uma estrada")
                self.achievements_manager.update_longest_road(self.tabletop.roads)
                self._update_turn_state()
                return True
        return False

    def _bot_build_city(self):
        """Bot upgrades a settlement to a city."""
        player = self.current_player
        buildables = self.tabletop.houses
        houses = [b for b in buildables if hasattr(b, 'level')]
        upgradable = [h for h in houses if h.level == 1 and h.owner == player]
        
        if upgradable:
            # Choose random from available
            best = random.choice(upgradable[:3])
            if best.try_build(player):
                SoundManager().play('construction')
                self.toast_manager.show(f"{player.name} atualizou para uma cidade")
                self._update_turn_state()
                return True
        return False

    def _bot_handle_discard(self):
        """Bot automatically selects resources to discard when >7."""
        player = self._discarding_player
        if not player or not player.is_bot:
            return
        
        bot = self.bot_deciders.get(player.id)
        if not bot:
            return
        
        discard_count = player.inventory.total() // 2
        selection = bot.select_discard_resources(discard_count)
        self._confirm_discard(selection)

    def _bot_handle_robber_move(self):
        """Bot automatically moves robber to steal from opponent."""
        player = self.current_player
        if not player.is_bot:
            return
        
        bot = self.bot_deciders.get(player.id)
        if not bot:
            return
        
        # Get all tiles except current robber tile
        all_tiles = self.tabletop.tiles
        available_tiles = [t for t in all_tiles if t != self.tabletop.robber_tile]
        
        if available_tiles:
            best_tile = bot.select_robber_tile(available_tiles)
            if best_tile:
                self.tabletop.move_robber(best_tile)
                self.awaiting_robber_tile = False
                SoundManager().play('ladrao_move')
