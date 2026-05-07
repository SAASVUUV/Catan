from .hexagon import Hexagon
from constants.types_colors import types_colors
from .road import Road
from .house import House
from .hover import Hover

class HexagonTile:

    def __init__(self, number, type, x, y, radius, x_tabletop, y_tabletop, tabletop):
        self.hexagon = Hexagon(radius,x,y, types_colors[type])
        self.terrain_type = type
        self.number = number
        self.vertices = []
        self.roads = []
        self.x_tabletop = x_tabletop
        self.y_tabletop = y_tabletop
        self.tabletop = tabletop
        self.hover = Hover(self.hexagon.collidepoint)

        self.house_top = None
        self.house_bottom = None
        self.house_top_left = None
        self.house_top_right = None
        self.house_bottom_left = None
        self.house_bottom_right = None

        self.road_left = None
        self.road_right = None
        self.road_top_left = None
        self.road_top_right = None
        self.road_bottom_right = None
        self.road_bottom_left = None

    def link(self):
        self.tile_left = self.tabletop[self.y_tabletop][self.x_tabletop-2] if self.x_tabletop > 1 else None
        self.tile_right = self.tabletop[self.y_tabletop][self.x_tabletop+2] if self.x_tabletop < 7 else None
        self.tile_left_top = self.tabletop[self.y_tabletop-1][self.x_tabletop-1] if self.x_tabletop > 0 and self.y_tabletop > 0 else None
        self.tile_right_top = self.tabletop[self.y_tabletop-1][self.x_tabletop+1] if self.x_tabletop < 8 and self.y_tabletop > 0 else None
        self.tile_left_bottom = self.tabletop[self.y_tabletop+1][self.x_tabletop-1] if self.x_tabletop > 0 and self.y_tabletop < 4 else None
        self.tile_right_bottom = self.tabletop[self.y_tabletop+1][self.x_tabletop+1] if self.x_tabletop < 8 and self.y_tabletop < 4 else None

    def create_houses(self):
        if(self.tile_left):
            if not self.house_top_left: self.house_top_left = self.tile_left.house_top_right
            if not self.house_bottom_left: self.house_bottom_left = self.tile_left.house_bottom_right
        if(self.tile_left_top):
            if not self.house_top_left: self.house_top_left = self.tile_left_top.house_bottom
            if not self.house_top: self.house_top = self.tile_left_top.house_bottom_right
        if(self.tile_right_top):
            if not self.house_top: self.house_top = self.tile_right_top.house_bottom_left
            if not self.house_top_right: self.house_top_right = self.tile_right_top.house_bottom

        if not self.house_top: self.house_top = House(self.hexagon.vertex_top)
        if not self.house_bottom: self.house_bottom = House(self.hexagon.vertex_bottom)
        if not self.house_top_left: self.house_top_left = House(self.hexagon.vertex_top_left)
        if not self.house_top_right: self.house_top_right = House(self.hexagon.vertex_top_right)
        if not self.house_bottom_left: self.house_bottom_left = House(self.hexagon.vertex_bottom_left)
        if not self.house_bottom_right: self.house_bottom_right = House(self.hexagon.vertex_bottom_right)

    def create_roads(self):
        if(self.tile_left): self.road_left = self.tile_left.road_right
        if(self.tile_left_top): self.road_top_left = self.tile_left_top.road_bottom_right
        if(self.tile_right_top): self.road_top_right = self.tile_right_top.road_bottom_left
        
        if not self.road_left: self.road_left = Road(self.hexagon.edge_left)
        if not self.road_top_left: self.road_top_left = Road(self.hexagon.edge_top_left)
        if not self.road_top_right: self.road_top_right = Road(self.hexagon.edge_top_right)
        if not self.road_right: self.road_right = Road(self.hexagon.edge_right)
        if not self.road_bottom_right: self.road_bottom_right = Road(self.hexagon.edge_bottom_right)
        if not self.road_bottom_left: self.road_bottom_left = Road(self.hexagon.edge_bottom_left)

    def extract_houses(self): return [self.house_bottom, self.house_top, self.house_bottom_left, self.house_bottom_right, self.house_top_left, self.house_top_right]
    def extract_roads(self): return [self.road_left, self.road_right, self.road_bottom_left, self.road_bottom_right, self.road_top_left, self.road_top_right]

    def update(self, dt):
        self.hover.update()
    def handle_event(self, event):
        self.hover.handle_event(event)

    def render(self, surface):
        self.hexagon.render(surface)