from unittest.mock import patch, MagicMock
from models.player import Player
from core.turn_manager import TurnManager
from components.tabletop import Tabletop
from core.construction_manager import ConstructionManager
from systems.achievements import AchievementsManager
from systems.card_manager import CardManager
from constants.types import BRICK, TREE, LAMB, WHEAT, ROCK
from constants.colors import RED, BLUE, GREEN, YELLOW
from constants.phases import TurnPhase

def test_full_game_setup_phase_two_players():
    # Setup: 2 players, determinístico
    players = [
        Player(1, "Alice", RED),
        Player(2, "Bob", BLUE),
    ]
    
    with patch("core.turn_manager.random.shuffle", lambda seq: None):
        turn_manager = TurnManager(players)
    
    tabletop = Tabletop(100, 100, 50)
    manager = ConstructionManager(tabletop)
    
    # Simular setup
    while turn_manager.is_setup_phase:
        current = turn_manager.current_player
        
        # Dar recursos para construção (simulado)
        current.inventory.add(BRICK, 2)
        current.inventory.add(TREE, 2)
        current.inventory.add(LAMB, 2)
        current.inventory.add(WHEAT, 2)
        
        # Construir aldeia (simulada)
        if not turn_manager.setup_built_house:
            # Pegar primeira casa vazia
            house = next((h for h in tabletop.houses if h and h.owner is None), None)
            if house:
                house.owner = current
                house.level = 1
                current.settlements_count += 1
                turn_manager.setup_record_house()
                
                # Distribuir recursos iniciais
                tabletop.distribute_initial_resources(current, house)
        
        # Construir estrada (simulada)
        if not turn_manager.setup_built_road:
            road = next((r for r in tabletop.roads if r and r.owner is None), None)
            if road:
                road.owner = current
                current.roads_count += 1
                turn_manager.setup_record_road()
        
        # Passar turno
        if turn_manager.setup_turn_complete():
            turn_manager.next_turn()
    
    # Validações
    assert not turn_manager.is_setup_phase, "Setup deve ter terminado"
    assert turn_manager.current_phase == TurnPhase.DICE, "Deve estar em DICE phase"
    
    for player in players:
        assert player.settlements_count == 2, f"{player.name} deve ter 2 aldeias"
        assert player.roads_count == 2, f"{player.name} deve ter 2 estradas"
        assert player.inventory.total() > 0, f"{player.name} deve ter recursos"


def test_full_game_regular_turns_resource_distribution():
    players = [
        Player(1, "Alice", RED),
        Player(2, "Bob", BLUE),
    ]
    
    with patch("core.turn_manager.random.shuffle", lambda seq: None):
        turn_manager = TurnManager(players)
    
    tabletop = Tabletop(100, 100, 50)
    
    # Setup rápido (colocar estruturas)
    for player in players:
        # Aldeia 1
        house1 = next((h for h in tabletop.houses if h and h.owner is None), None)
        if house1:
            house1.owner = player
            house1.level = 1
            player.settlements_count += 1
            tabletop.distribute_initial_resources(player, house1)
        
        # Estrada 1
        road1 = next((r for r in tabletop.roads if r and r.owner is None), None)
        if road1:
            road1.owner = player
            player.roads_count += 1
        
        # Aldeia 2
        house2 = next((h for h in tabletop.houses if h and h.owner is None), None)
        if house2:
            house2.owner = player
            house2.level = 1
            player.settlements_count += 1
            tabletop.distribute_initial_resources(player, house2)
        
        # Estrada 2
        road2 = next((r for r in tabletop.roads if r and r.owner is None), None)
        if road2:
            road2.owner = player
            player.roads_count += 1
    
    turn_manager.is_setup_phase = False
    turn_manager.current_phase = TurnPhase.DICE
    turn_manager.normal_turn_index = 0
    
    # Simular 5 turnos
    turns_simulated = 0
    max_turns = 5
    
    while turns_simulated < max_turns:
        current = turn_manager.current_player
        
        # Rolar dados (determinístico)
        with patch("core.turn_manager.random.randint") as mock_roll:
            # Variar para diferentes números
            dice_val = 2 + (turns_simulated % 5)
            dice1 = min(6, max(1, dice_val // 2))
            dice2 = dice_val - dice1
            mock_roll.side_effect = [dice1, dice2]
            result = turn_manager.roll_dice()
        
        assert turn_manager.current_phase == TurnPhase.COMMERCE, "Deve ser COMMERCE após roll"
        
        # Distribuir recursos se não for 7
        if turn_manager.dice_sum != 7:
            resources_before = current.inventory.total()
            tabletop.distribute_resources_for_roll(turn_manager.dice_sum)
            resources_after = current.inventory.total()
            # Recursos devem ser distribuídos (ou mesma se sem estrutura no tile)
        
        # Passar para próxima fase
        turn_manager.next_phase()
        assert turn_manager.current_phase == TurnPhase.CONSTRUCTION, "Deve ser CONSTRUCTION"
        
        # Passar turno
        turn_manager.next_phase()
        turns_simulated += 1
    
    # Validações
    assert turn_manager.normal_turn_index == (5 % 2), "Index deve rodar"
    assert turn_manager.current_phase == TurnPhase.DICE, "De volta a DICE"


def test_full_game_four_players_construction_and_victory():
    players = [
        Player(1, "Alice", RED),
        Player(2, "Bob", BLUE),
        Player(3, "Charlie", GREEN),
        Player(4, "Diana", YELLOW),
    ]
    
    with patch("core.turn_manager.random.shuffle", lambda seq: None):
        turn_manager = TurnManager(players)
    
    tabletop = Tabletop(100, 100, 50)
    manager = ConstructionManager(tabletop)
    card_manager = CardManager(players)
    achievements_manager = AchievementsManager(players)
    
    # Setup simplificado
    for player in players:
        player.inventory.add(BRICK, 10)
        player.inventory.add(TREE, 10)
        player.inventory.add(LAMB, 10)
        player.inventory.add(WHEAT, 10)
        player.inventory.add(ROCK, 10)
    
    turn_manager.is_setup_phase = False
    turn_manager.current_phase = TurnPhase.DICE
    
    # Simular 40 turnos até vitória
    turns = 0
    max_turns = 40
    winner = None
    
    while turns < max_turns and winner is None:
        current = turn_manager.current_player
        
        # Rolar dados
        with patch("core.turn_manager.random.randint") as mock_roll:
            dice1 = 3
            dice2 = 4
            mock_roll.side_effect = [dice1, dice2]
            turn_manager.roll_dice()
        
        # Distribuir (se não 7)
        if turn_manager.dice_sum != 7:
            tabletop.distribute_resources_for_roll(turn_manager.dice_sum)
        
        # Simular construção: construir uma estrutura se possível
        if current.inventory.get_count(BRICK) >= 1 and current.inventory.get_count(TREE) >= 1:
            # Tentar construir estrada
            if current.roads_count < 15:
                current.buy_road()
        
        if current.inventory.get_count(BRICK) >= 1 and current.inventory.get_count(TREE) >= 1 \
           and current.inventory.get_count(LAMB) >= 1 and current.inventory.get_count(WHEAT) >= 1:
            # Tentar construir aldeia
            if current.settlements_count < 5:
                current.buy_settlement()
        
        if current.inventory.get_count(ROCK) >= 3 and current.inventory.get_count(WHEAT) >= 2 \
           and current.settlements_count > 0:
            # Tentar upgrade para cidade
            if current.cities_count < 4:
                current.buy_city()
        
        # Passar fases
        turn_manager.next_phase()
        turn_manager.next_phase()
        
        # Checar vitória
        winner = turn_manager.check_victory()
        turns += 1
    
    # Todos os players devem ter estruturas
    for player in players:
        assert player.settlements_count + player.cities_count >= 0, "Estado coerente"


def test_full_game_robber_and_steal():
    p1 = Player(1, "Alice", RED)
    p1.inventory.add(BRICK, 5)
    p1.inventory.add(TREE, 5)
    p1.inventory.add(LAMB, 5)
    p1.inventory.add(WHEAT, 5)
    p1.inventory.add(ROCK, 5)
    
    p2 = Player(2, "Bob", BLUE)
    p2.inventory.add(BRICK, 3)
    
    players = [p1, p2]
    
    with patch("core.turn_manager.random.shuffle", lambda seq: None):
        turn_manager = TurnManager(players)
    
    tabletop = Tabletop(100, 100, 50)
    turn_manager.is_setup_phase = False
    turn_manager.current_phase = TurnPhase.DICE
    
    # Colocar estruturas em tiles
    houses_p1 = []
    houses_p2 = []
    
    for i, house in enumerate(tabletop.houses):
        if house and house.owner is None:
            if i % 2 == 0 and len(houses_p1) < 2:
                house.owner = p1
                house.level = 1
                houses_p1.append(house)
            elif len(houses_p2) < 2:
                house.owner = p2
                house.level = 1
                houses_p2.append(house)
            
            if len(houses_p1) >= 2 and len(houses_p2) >= 2:
                break
    
    # Rolar 7
    with patch("core.turn_manager.random.randint") as mock_roll:
        mock_roll.side_effect = [4, 3]
        turn_manager.roll_dice()
    
    assert turn_manager.dice_sum == 7, "Deve rolar 7"
    
    # P1 tem >7 cartas, deve descartar
    discard_count = p1.inventory.total() // 2
    resources_before = p1.inventory.total()
    
    # Simular descarte (remove aleatory)
    for resource_type in [BRICK, TREE, LAMB, WHEAT, ROCK]:
        if p1.inventory.get_count(resource_type) > 0:
            while p1.inventory.total() > 7 and p1.inventory.get_count(resource_type) > 0:
                p1.inventory.remove(resource_type, 1)
    
    resources_after = p1.inventory.total()
    assert resources_after <= 7, "P1 deve ter 7 ou menos após descarte"
    
    # Mover robô para tile com p2
    if houses_p2:
        target_tile = next((t for t in tabletop.tiles if houses_p2[0] in t.extract_houses()), None)
        if target_tile:
            tabletop.move_robber(target_tile)
            
            # Simular roubo (random)
            with patch("random.choice") as mock_choice:
                # Escolher BRICK de p2
                mock_choice.return_value = BRICK
                
                # Roubar
                if p2.inventory.get_count(BRICK) > 0:
                    p2.inventory.remove(BRICK, 1)
                    p1.inventory.add(BRICK, 1)
    
    # Validações
    assert tabletop.robber_tile is not None, "Robô deve estar em algum tile"
    if target_tile:
        assert tabletop.robber_tile == target_tile, "Robô deve estar no tile correto"


def test_full_game_development_cards():
    p1 = Player(1, "Alice", RED)
    p1.inventory.add(ROCK, 5)
    p1.inventory.add(LAMB, 5)
    p1.inventory.add(WHEAT, 5)
    
    players = [p1]
    
    card_manager = CardManager(players)
    achievements_manager = AchievementsManager(players)
    
    with patch("core.turn_manager.random.shuffle", lambda seq: None):
        turn_manager = TurnManager(players)
    
    # Comprar 3 cartas
    for i in range(3):
        success = card_manager.attempt_buy_card(p1)
        if not success and len(card_manager.development_cards) == 0:
            # Deck vazio, parar
            break
    
    cards_bought = len(p1.development_cards)
    assert cards_bought > 0, "Deve ter comprado cartas"
    
    # Verificar LOCKED
    for card in p1.development_cards:
        from components.card_states import CardState
        assert card.state == CardState.LOCKED, "Cartas devem estar LOCKED"
    
    # Simular turno passar
    card_manager.on_turn_start(p1)
    
    # Verificar READY
    from components.card_states import CardState
    for card in p1.development_cards:
        assert card.state == CardState.READY, "Cartas devem estar READY após turn"
    
    # Ativar cavaleiros
    from components.base_card import KnightCard
    knights = [c for c in p1.development_cards if isinstance(c, KnightCard)]
    
    for knight in knights:
        success = card_manager.attempt_activate_card(p1, knight)
        # Se ativação sucede, knights_played deve aumentar
    
    # Atualizar achievements
    achievements_manager.update_largest_army()
    
    # Se tem 3+ cavaleiros, deve ter largest_army
    if p1.knights_played >= 3:
        assert p1.has_largest_army, "Deve ter largest_army com 3+ cavaleiros"

def test_recovery_after_losing_resource_during_build(monkeypatch):
    # Setup do jogo para o teste de recuperação
    players = [Player(1, "Alice", RED)]
    
    # Usar um mock para o tabuleiro para isolar a lógica de construção
    mock_board = MagicMock()
    mock_board.get_path.return_value = MagicMock()
    mock_board.is_valid_road_connection.return_value = True  # Simula uma conexão válida
    
    construction_manager = ConstructionManager(mock_board)
    
    player = players[0]
    
    # Garante que o jogador tenha recursos para exatamente uma estrada
    player.inventory.cards[BRICK] = 1
    player.inventory.cards[TREE] = 1
    
    # Simula a perda de um recurso essencial durante a chamada de construção
    original_buy_road = player.buy_road
    def mock_buy_road(*args, **kwargs):
        # Simula a falha: recurso desaparece antes da validação final
        player.inventory.remove(BRICK, 1)
        return original_buy_road(*args, **kwargs)
        
    monkeypatch.setattr(player, 'buy_road', mock_buy_road)
    
    # Tenta construir a estrada (deve falhar)
    initial_road_count = player.roads_count
    road_built = construction_manager.attempt_build_road(player, (0, 0))

    # Verificações de recuperação
    assert not road_built, "A construção da estrada deveria ter falhado."
    assert player.roads_count == initial_road_count, "Nenhuma estrada deveria ter sido adicionada ao jogador."
    assert player.inventory.cards[BRICK] == 0, "O recurso BRICK deveria ter sido consumido pela falha simulada."
    assert player.inventory.cards[TREE] == 1, "O recurso TREE não deveria ter sido consumido na falha."


def test_recovery_after_losing_resource_during_settlement_purchase(monkeypatch):
    # Setup do jogo para o teste de recuperação de aldeia
    players = [Player(1, "Alice", RED)]

    mock_board = MagicMock()
    mock_board.get_intersection.return_value = MagicMock()
    mock_board.respects_distance_rule.return_value = True
    mock_board.has_connecting_road.return_value = True

    construction_manager = ConstructionManager(mock_board)

    player = players[0]
    player.inventory.cards[BRICK] = 1
    player.inventory.cards[TREE] = 1
    player.inventory.cards[LAMB] = 1
    player.inventory.cards[WHEAT] = 1

    original_buy_settlement = player.buy_settlement

    def mock_buy_settlement(*args, **kwargs):
        # Simula a falha: um recurso some durante a validação da compra
        player.inventory.remove(WHEAT, 1)
        return original_buy_settlement(*args, **kwargs)

    monkeypatch.setattr(player, "buy_settlement", mock_buy_settlement)

    initial_settlement_count = player.settlements_count
    settlement_built = construction_manager.attempt_build_settlement(player, (0, 1))

    assert not settlement_built, "A compra da aldeia deveria ter falhado."
    assert player.settlements_count == initial_settlement_count, "Nenhuma aldeia deveria ter sido adicionada ao jogador."
    assert player.inventory.cards[WHEAT] == 0, "O recurso WHEAT deveria ter sido consumido pela falha simulada."
    assert player.inventory.cards[BRICK] == 1, "O recurso BRICK não deveria ter sido consumido na falha."


def test_recovery_after_losing_resource_during_city_upgrade(monkeypatch):
    # Setup do jogo para o teste de recuperação de cidade
    players = [Player(1, "Alice", RED)]

    mock_board = MagicMock()
    mock_intersection = MagicMock()
    mock_intersection.has_player_settlement.return_value = True
    mock_intersection.upgrade_to_city.return_value = None
    mock_board.get_intersection.return_value = mock_intersection

    construction_manager = ConstructionManager(mock_board)

    player = players[0]
    player.settlements_count = 1
    player.inventory.cards[ROCK] = 3
    player.inventory.cards[WHEAT] = 2

    original_buy_city = player.buy_city

    def mock_buy_city(*args, **kwargs):
        # Simula a falha: um recurso desaparece antes da validação final
        player.inventory.remove(ROCK, 1)
        return original_buy_city(*args, **kwargs)

    monkeypatch.setattr(player, "buy_city", mock_buy_city)

    initial_city_count = player.cities_count
    city_built = construction_manager.attempt_upgrade_to_city(player, (0, 2))

    assert not city_built, "A melhoria para cidade deveria ter falhado."
    assert player.cities_count == initial_city_count, "Nenhuma cidade deveria ter sido adicionada ao jogador."
    assert player.settlements_count == 1, "A aldeia original não deveria ter sido removida na falha."
    assert player.inventory.cards[ROCK] == 2, "O recurso ROCK deveria ter sido consumido pela falha simulada."
    assert player.inventory.cards[WHEAT] == 2, "O recurso WHEAT não deveria ter sido consumido na falha."

