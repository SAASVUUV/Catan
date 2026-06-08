import pygame
from components.modal import Modal
from components.button import Button
from constants.colors import YELLOW, GREEN_FOREST, BROWN_DARK
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.resources import resource_path


class RoadBuildingDialog(Modal):
    def __init__(self, owner, tabletop, on_confirm=None, on_cancel=None, width: int = None, height: int = None, overlay_fullscreen: bool = False):
        # Tamanho dinâmico do modal
        w = width or int(SCREEN_WIDTH * 0.65)
        h = height or int(SCREEN_HEIGHT * 0.16)
        super().__init__(w, h, title="Construção de Estradas", overlay_fullscreen=overlay_fullscreen)
        self.owner = owner
        self.tabletop = tabletop
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        # Posição do dialog na área inferior
        margin_bottom = int(SCREEN_HEIGHT * 0.05)
        self.rect.x = (SCREEN_WIDTH - self.width) // 2
        self.rect.y = SCREEN_HEIGHT - self.height - margin_bottom
        self.x, self.y = self.rect.x, self.rect.y

        self.selected = []
        
        # --- CORREÇÃO DO POSICIONAMENTO DOS BOTÕES ---
        
        # Dimensões e margens
        btn_h = 36
        btn_w_confirm = 120
        btn_w_cancel = 100
        margin_x = 40 # Espaço entre o botão e a borda lateral
        margin_y = 25 # Espaço entre o botão e a borda inferior do modal

        # Calcula a posição Y garantindo que fique dentro do modal (na parte de baixo)
        by = self.rect.bottom - btn_h - margin_y

        cancel_x = self.rect.left + margin_x
        confirm_x = self.rect.right - btn_w_confirm - margin_x

        self.cancel_btn = Button(cancel_x, by, btn_w_cancel, btn_h, "Cancelar")
        self.confirm_btn = Button(confirm_x, by, btn_w_confirm, btn_h, "Confirmar")

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # button clicks
            if self.cancel_btn.handle_event(event):
                if self.on_cancel:
                    self.on_cancel()
                self.hide()
                return True
            if self.confirm_btn.handle_event(event) and len(self.selected) == 2:
                if self.on_confirm:
                    self.on_confirm(self.selected.copy())
                self.hide()
                return True

            # click on board to pick an edge
            mx, my = event.pos
            for road in self.tabletop.roads:
                if road is None:
                    continue
                if road.collidepoint((mx, my)):
                    # ignore clicks on roads that are already built
                    if getattr(road, 'owner', None) is not None:
                        return True
                    # Determine if this road is selectable:
                    # - valid by normal placement rules, OR
                    # - adjacent to a previously selected road (so it can be placed
                    #   as the second road in the pair).
                    try:
                        valid_by_rules = road._can_place_road(self.owner, self.tabletop.roads, force_free=True)
                    except Exception:
                        valid_by_rules = False

                    valid_by_selected = False
                    if not valid_by_rules and self.selected:
                        # allow adjacency to already-selected roads
                        for s in self.selected:
                            ha, hb = getattr(road, 'house_a', None), getattr(road, 'house_b', None)
                            sa, sb = getattr(s, 'house_a', None), getattr(s, 'house_b', None)
                            if ha and (ha is sa or ha is sb):
                                valid_by_selected = True
                                break
                            if hb and (hb is sa or hb is sb):
                                valid_by_selected = True
                                break

                    if not (valid_by_rules or valid_by_selected):
                        return True

                    if road in self.selected:
                        self.selected.remove(road)
                    else:
                        if len(self.selected) < 2:
                            self.selected.append(road)
                    return True

        return True

    def update(self, dt: float):
        # ensure selection never grows beyond 2
        if len(self.selected) > 2:
            self.selected = self.selected[:2]
        self.confirm_btn.enabled = (len(self.selected) == 2)
        self.confirm_btn.update()
        self.cancel_btn.update()

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        # draw modal overlay and box
        super().render(surface)

        # highlight valid edges on the board
        # Only draw selected roads (avoid greying out the whole board)
        for road in self.selected:
            if road is None:
                continue
            pygame.draw.line(surface, GREEN_FOREST, (road.x0, road.y0), (road.x1, road.y1), 8)

        # draw status inside modal with larger font and centered
        scale = SCREEN_HEIGHT / 600.0
        caminho_fonte = resource_path('assets', 'fonts', 'MedievalSharp-Regular.ttf')
        font = pygame.font.Font(caminho_fonte,  max(16, int(20 * scale)))
        status = f"Estradas selecionadas: {len(self.selected)}/2"
        status_surf = font.render(status, True, BROWN_DARK)
        status_x = self.rect.centerx - status_surf.get_width() // 2
        status_y = self.rect.top + 50
        surface.blit(status_surf, (status_x, status_y))

        # draw confirm/cancel buttons
        self.confirm_btn.render(surface)
        self.cancel_btn.render(surface)
