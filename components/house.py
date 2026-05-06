from .circle import Circle

class House:

    def __init__(self, pos, color=(0,0,0), radius=10):
        self.x = pos[0]
        self.y = pos[1]
        self.circle = Circle(pos[0], pos[1], radius, (255,0,0)) 

    def render(self, window):
        self.circle.render(window)
    def handle_event(self, event):
        pass
    def update(self, dt):
        pass