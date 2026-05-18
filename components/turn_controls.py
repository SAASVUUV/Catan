import pygame
from .button import Button
from .dice import Dice
from constants.colors import BEIGE_LIGHT, BROWN_DARK, BLACK
from constants.phases import TurnPhase


PHASE_LABELS = {
    TurnPhase.DICE: "Dados",
    TurnPhase.COMMERCE: "Comércio",
    TurnPhase.CONSTRUCTION: "Construção",
}


class TurnControls:
    def __init__(self, x, y, width, scale: float = 1.0):
        self.x = x
        self.y = y
        self.width = width
        self.height = int(140 * scale)
        self.phase = TurnPhase.DICE
        self.is_setup = True

        font_size = int(22 * scale)
        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, font_size)

        dice_size = int(48 * scale)
        dice_spacing = int(10 * scale)
        dice_total_width = dice_size * 2 + dice_spacing
        self.dice = Dice(x + (width - dice_total_width) // 2, y + int(40 * scale), size=dice_size)

        btn_width = width - int(20 * scale)
        btn_height = int(40 * scale)
        btn_font = int(20 * scale)
        btn_y = y + self.height - btn_height - int(10 * scale)
        btn_x = x + int(10 * scale)
        self.btn_roll = Button(btn_x, btn_y, btn_width, btn_height, "Lançar Dados", font_size=btn_font)
        self.btn_next = Button(btn_x, btn_y, btn_width, btn_height, "Próxima Fase", font_size=btn_font)
        self.btn_end = Button(btn_x, btn_y, btn_width, btn_height, "Terminar Turno", font_size=btn_font)

    def set_state(self, phase, dice_result, is_setup):
        self.phase = phase
        self.is_setup = is_setup
        if dice_result:
            self.dice.set_values(dice_result[0], dice_result[1])
        else:
            self.dice.hide()

    def handle_event(self, event):
        if self.is_setup:
            return None

        if self.phase == TurnPhase.DICE:
            if self.btn_roll.handle_event(event):
                return 'roll'
        elif self.phase == TurnPhase.COMMERCE:
            if self.btn_next.handle_event(event):
                return 'next_phase'
        elif self.phase == TurnPhase.CONSTRUCTION:
            if self.btn_end.handle_event(event):
                return 'end_turn'
        return None

    def update(self):
        if self.is_setup:
            return
        if self.phase == TurnPhase.DICE:
            self.btn_roll.update()
        elif self.phase == TurnPhase.COMMERCE:
            self.btn_next.update()
        elif self.phase == TurnPhase.CONSTRUCTION:
            self.btn_end.update()

    def render(self, surface):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, BEIGE_LIGHT, rect, border_radius=8)
        pygame.draw.rect(surface, BROWN_DARK, rect, width=2, border_radius=8)

        if self.is_setup:
            setup_text = self.font.render("Fase de Setup", True, BROWN_DARK)
            text_x = self.x + (self.width - setup_text.get_width()) // 2
            text_y = self.y + (self.height - setup_text.get_height()) // 2
            surface.blit(setup_text, (text_x, text_y))
            return

        phase_label = PHASE_LABELS.get(self.phase, "")
        phase_text = self.font.render(f"Fase: {phase_label}", True, BROWN_DARK)
        phase_x = self.x + (self.width - phase_text.get_width()) // 2
        surface.blit(phase_text, (phase_x, self.y + 10))

        if self.dice.visible:
            self.dice.render(surface)

        if self.phase == TurnPhase.DICE:
            self.btn_roll.render(surface)
        elif self.phase == TurnPhase.COMMERCE:
            self.btn_next.render(surface)
        elif self.phase == TurnPhase.CONSTRUCTION:
            self.btn_end.render(surface)
