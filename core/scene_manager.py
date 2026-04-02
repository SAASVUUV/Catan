class SceneManager:
    def __init__(self):
        self.stack = []
 
    def push(self, scene):
        self.stack.append(scene)
 
    def pop(self):
        if self.stack:
            self.stack.pop()
 
    def replace(self, scene):
        self.pop()
        self.push(scene)
 
    @property
    def current(self):
        return self.stack[-1] if self.stack else None