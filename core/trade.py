from constants.types import GENERIC

class BankTrade:
    DEFAULT_RATIO = 4

    @staticmethod
    def get_ratio(player, resource: int, ports: list) -> int:
        best_ratio = BankTrade.DEFAULT_RATIO
        for port in ports:
            if port.house1.owner != player and port.house2.owner != player:
                continue
            if port.type == resource:
                return port.ratio
            if port.type == GENERIC and port.ratio < best_ratio:
                best_ratio = port.ratio
        return best_ratio

    @staticmethod
    def can_execute(player, give_type: int, give_count: int, receive_type: int, ports: list) -> bool:
        ratio = BankTrade.get_ratio(player, give_type, ports)
        return give_count >= ratio and player.inventory.has(give_type, give_count)

    @staticmethod
    def execute(player, give_type: int, give_count: int, receive_type: int) -> bool:
        if not player.inventory.remove(give_type, give_count):
            return False
        player.inventory.add(receive_type, 1)
        return True


class TradeOffer:
    def __init__(self, proposer, target, offering: dict, requesting: dict):
        self.proposer = proposer
        self.target = target
        self.offering = offering
        self.requesting = requesting


class PlayerTrade:
    @staticmethod
    def can_propose(offer: TradeOffer) -> bool:
        if not offer.offering:
            return True
        return offer.proposer.inventory.has_multiple(offer.offering)

    @staticmethod
    def can_accept(offer: TradeOffer) -> bool:
        if not offer.requesting:
            return True
        return offer.target.inventory.has_multiple(offer.requesting)

    @staticmethod
    def execute(offer: TradeOffer) -> bool:
        if not PlayerTrade.can_propose(offer) or not PlayerTrade.can_accept(offer):
            return False
        for res, count in offer.offering.items():
            offer.proposer.inventory.remove(res, count)
            offer.target.inventory.add(res, count)
        for res, count in offer.requesting.items():
            offer.target.inventory.remove(res, count)
            offer.proposer.inventory.add(res, count)
        return True
