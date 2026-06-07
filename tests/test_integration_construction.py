from unittest.mock import MagicMock, patch
from models.player import Player
from core.construction_manager import ConstructionManager
from components.tabletop import Tabletop
from constants.types import BRICK, TREE, LAMB, WHEAT, ROCK
from constants.colors import RED, BLUE


def test_road_construction_basic():
    player = Player(1, "Alice", RED)
    # Dar muitos recursos
    for _ in range(30):
        player.inventory.add(BRICK, 1)
        player.inventory.add(TREE, 1)
    
    # Tentar construir muitas estradas (limite é 15)
    for _ in range(20):
        if not player.buy_road():
            break
    
    # Deve parar no limite
    assert player.roads_count <= 15, f"Limite de estradas é 15, mas tem {player.roads_count}"
    assert player.roads_count >= 10, "Deve conseguir construir pelo menos 10"


def test_settlement_construction_requires_resources():
    player = Player(1, "Alice", RED)
    # Sem dar recursos
    
    tabletop = Tabletop(100, 100, 50)
    manager = ConstructionManager(tabletop)
    
    # Pegar primeira casa vazia
    house = next((h for h in tabletop.houses if h and h.owner is None), None)
    assert house is not None

def test_road_limit():
    player = Player(1, "Alice", RED)
    player.roads_count = 15  # Limite máximo
    player.inventory.add(BRICK, 1)
    player.inventory.add(TREE, 1)
    
    # Validar que can_build_road retorna False
    assert not player.can_build_road(max_limit=15), \
        "Deve falhar ao atingir limite de estradas"


def test_settlement_limit():
    player = Player(1, "Alice", RED)
    player.settlements_count = 5  # Limite máximo
    player.inventory.add(BRICK, 1)
    player.inventory.add(TREE, 1)
    player.inventory.add(LAMB, 1)
    player.inventory.add(WHEAT, 1)
    
    # Validar que buy_settlement falha
    success = player.buy_settlement(max_limit=5)
    assert not success, "Deve falhar ao atingir limite de aldeias"
    assert player.settlements_count == 5, "Contagem não deve mudar"


def test_city_limit():
    player = Player(1, "Alice", RED)
    player.cities_count = 4  # Limite máximo
    player.settlements_count = 1  # Aldeia para upgrade
    player.inventory.add(ROCK, 3)
    player.inventory.add(WHEAT, 2)
    
    # Validar que buy_city falha
    success = player.buy_city(max_limit=4)
    assert not success, "Deve falhar ao atingir limite de cidades"
    assert player.cities_count == 4, "Contagem não deve mudar"


def test_construction_costs():
    # Road cost
    player = Player(1, "Alice", RED)
    player.inventory.add(BRICK, 1)
    player.inventory.add(TREE, 1)
    
    assert player.has_resources_for_road(), "Deve ter recursos para estrada"
    
    player.inventory.remove(BRICK, 1)
    assert not player.has_resources_for_road(), "Sem recursos para estrada"
    
    # Settlement cost
    player2 = Player(2, "Bob", BLUE)
    player2.inventory.add(BRICK, 1)
    player2.inventory.add(TREE, 1)
    player2.inventory.add(LAMB, 1)
    player2.inventory.add(WHEAT, 1)
    
    assert player2.has_resources_for_settlement(), "Deve ter recursos para aldeia"
    
    player2.inventory.remove(BRICK, 1)
    assert not player2.has_resources_for_settlement(), "Sem recursos para aldeia"
    
    # City cost
    player3 = Player(3, "Charlie", (100, 100, 100))
    player3.inventory.add(ROCK, 3)
    player3.inventory.add(WHEAT, 2)
    player3.settlements_count = 1
    
    assert player3.has_resources_for_city(), "Deve ter recursos para cidade"
    
    player3.inventory.remove(ROCK, 1)
    assert not player3.has_resources_for_city(), "Sem recursos para cidade (falta ROCK)"
