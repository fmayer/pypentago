from pypentago import core

class ServerGame(core.Game):
    def __init__(self, name):
        core.Game.__init__(self)
        self.name = name
    
    def serialize(self):
        return {
            'name': self.name,
            'players': [p.serialize() for p in self.players],
            'uid': uid
        }
    
