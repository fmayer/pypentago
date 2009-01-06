# pyPentago - a board game
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

from pypentago.server.game import Game


class Room:
    """ This class represents a room. 
    
    The name of the room is its unique identifier, so you may not create two 
    rooms with the same name.
    
    desc is an optional description of the room.
    """
    def __init__(self, name, desc=None):
        self.players = []
        self.name = name
        self.desc = desc
        self.games = []
    
    def join(self, player):
        """ Add player to the room, making him receive all the 
        messages that are sent to it """
        self.players.append(player)
        self.sync_players()
        player.send("ROOMGAMES", (self.name, self.get_games()))
        
    def send_all(self, *args, **kwargs):
        """ Execute send on all players with the passed arguments and 
        keyword arguments. """
        for player in self.players:
            player.send(*args, **kwargs)
        
    def say_room(self, player, text):
        """ Send a message to all of the players in the room """
        self.send_all("MSG", (self.name, text))
    
    def get_games(self):
        """ Get the games in a form sendable to clients. """
        send = []
        for id, game in enumerate(self.games):
            if not game.full:
                send.append((id, game.name, game.players[0].name, 
                         game.players[0].database_player.current_rating, 
                         game.full, game.ranked))
        return send
    
    def sync_games(self):
        """ Synchronize games with clients. """
        self.send_all("ROOMGAMES", (self.name, self.get_games()))
    
    def sync_players(self):
        """ Synchronize players with all players in the room. Has 
        to be called when a player joins """
        players = [player.name for player in self.players]
        self.send_all("PLAYERS", (self.room_id, players))
    
    def open_game(self, player, game_name, ranked):
        """ Open a game visible in the room """
        self.games.append(Game(player, game_name, ranked))
