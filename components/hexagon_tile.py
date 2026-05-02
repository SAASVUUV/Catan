from .hexagon import Hexagon

class HexagonTile:

    def __init__(self, number, type, x, y, radius, x_tabletop, y_tabletop, tabletop):
        self.hexagon = Hexagon(x,y,radius)
        self.terrain_type = type
        self.number = number
        self.vertices = []
        self.edges = []
        self.x_tabletop = x_tabletop
        self.y_tabletop = y_tabletop
        self.tabletop = tabletop
    
        self.left_tile = self.tabletop[self.y_tabletop][self.x_tabletop-2] if self.x_tabletop > 1 else None
        self.right_tile = self.tabletop[self.y_tabletop][self.x_tabletop+2] if self.x_tabletop < 7 else None
        self.left_top_tile = self.tabletop[self.y_tabletop-1][self.x_tabletop-1] if self.x_tabletop > 0 and self.y_tabletop > 0 else None
        self.right_top_tile = self.tabletop[self.y_tabletop-1][self.x_tabletop+1] if self.x_tabletop < 8 and self.y_tabletop > 0 else None
        self.left_bottom_tile = self.tabletop[self.y_tabletop-1][self.x_tabletop-1] if self.x_tabletop > 0 and self.y_tabletop < 4 else None
        self.right_bottom_tile = self.tabletop[self.y_tabletop-1][self.x_tabletop+1] if self.x_tabletop < 8 and self.y_tabletop < 4 else None

    def addVertices(self, vertex): 
        self.vertices += vertex
        vertex.addHexagon(self)
    def addEdges(self, edge): 
        self.edges += edge
        edge.addHexagon(self)

    def update(self):
        pass
    def handle_event(self):
        pass

    def collidepoint(self, point):
        pass

    def render(self, surface):
        self.hexagon.render(surface)