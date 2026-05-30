from collections import defaultdict


def calculate_longest_road(player, all_roads) -> int:
    """
    Calcula o comprimento da maior cadeia de estradas conectadas do jogador.

    Regras:
    - Estradas são conectadas pelos endpoints (house_a, house_b)
    - Se uma casa pertence a outro jogador, ela "corta" a estrada
    - Retorna o maior caminho simples (sem repetir estradas)
    """
    player_roads = [r for r in all_roads if r.owner is player]
    if not player_roads:
        return 0

    graph = defaultdict(list)
    for road in player_roads:
        if road.house_a and road.house_b:
            graph[road.house_a].append((road.house_b, road))
            graph[road.house_b].append((road.house_a, road))

    def dfs(house, visited_roads):
        if house.owner is not None and house.owner is not player:
            return 0

        max_length = 0
        for neighbor, road in graph[house]:
            if road not in visited_roads:
                visited_roads.add(road)
                length = 1 + dfs(neighbor, visited_roads)
                max_length = max(max_length, length)
                visited_roads.remove(road)
        return max_length

    longest = 0
    for road in player_roads:
        for start_house in [road.house_a, road.house_b]:
            if start_house:
                visited = {road}
                length = 1 + dfs(start_house, visited)
                longest = max(longest, length)

    return longest
