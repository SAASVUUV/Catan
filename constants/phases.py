from enum import IntEnum


class TurnPhase(IntEnum):
    DICE = 0         # Lançar dados
    COMMERCE = 1     # Comércio (trocas)
    CONSTRUCTION = 2 # Construção
