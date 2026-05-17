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
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.width = width
        self.height = 105
        self.phase = TurnPhase.DICE
        self.is_setup = True

        caminho_fonte = "./assets/fonts/MedievalSharp-Regular.ttf"
        self.font = pygame.font.Font(caminho_fonte, 14)

        self.dice = Dice(x + (width - 74) // 2, y + 30, size=32)

        btn_width = width - 20
        btn_y = y + 70
        self.btn_roll = Button(x + 10, btn_y, btn_width, 28, "Lançar Dados", font_size=14)
        self.btn_next = Button(x + 10, btn_y, btn_width, 28, "Próxima Fase", font_size=14)
        self.btn_end = Button(x + 10, btn_y, btn_width, 28, "Terminar Turno", font_size=14)

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
            surface.blit(setup_text, (text_x, self.y + 40))
            return

        phase_label = PHASE_LABELS.get(self.phase, "")
        phase_text = self.font.render(f"Fase: {phase_label}", True, BROWN_DARK)
        phase_x = self.x + (self.width - phase_text.get_width()) // 2
        surface.blit(phase_text, (phase_x, self.y + 8))

        if self.dice.visible:
            self.dice.render(surface)
            # dice_sum = self.dice.die1 + self.dice.die2
            # sum_text = self.font.render(f"= {dice_sum}", True, BLACK)
            # sum_x = self.dice.x + 74 + 5
            # surface.blit(sum_text, (sum_x, self.y + 40))

        if self.phase == TurnPhase.DICE:
            self.btn_roll.render(surface)
        elif self.phase == TurnPhase.COMMERCE:
            self.btn_next.render(surface)
        elif self.phase == TurnPhase.CONSTRUCTION:
            self.btn_end.render(surface)
