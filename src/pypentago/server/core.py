# pypentago - a board game
# Copyright (C) 2008 Florian Mayer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from pypentago import core

class ServerGame(core.Game):
    def __init__(self, name, uid):
        core.Game.__init__(self)
        self.name = name
        self.uid = uid
    
    def serialize(self):
        return {
            'name': self.name,
            'players': [p.serialize() for p in self.players],
            'uid': self.uid
        }
    

class ServerPlayer(core.RemotePlayer):
    def player_quit(self, player):
        core.RemotePlayer.player_quit(self, player)
        self.conn.server.remove_game(self.game)
