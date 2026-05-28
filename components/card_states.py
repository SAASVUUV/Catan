from enum import Enum


class CardState(Enum):
    LOCKED = "locked"
    READY = "ready"
    USED = "used"

    def __str__(self):
        return self.value
