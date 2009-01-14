from pypentago import core

class ServerGame(core.Game):
    def __init__(self, name):
        core.Game.__init__(self)
        self.name = name
    
