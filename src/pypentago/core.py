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


import sys
import os
import random
import itertools

import depr

from pypentago import CW, CCW
from pypentago.exceptions import (InvalidTurn, SquareNotEmpty, NotYourTurn, 
                                  GameFull)


try:
    from pypentago._board import Board
    EXTENSION_MODULE = True
except ImportError:
    from pypentago.board import Board
    EXTENSION_MODULE = False


class Observer(object):
    def display_turn(self, turn):
        pass
    
    def game_over(winner, loser):
        pass
    
    def display_msg(self, author, msg):
        pass
    
    def player_quit(self, opponent):
        pass
    
    def player_joined(self, player):
        pass

        
class Player(object):
    """ The Player is the one that is interacting with the Game. """
    def __init__(self, name=None):
        self.game = None
        self.uid = None
        self.cmd = {'TURN': self.do_turn,
                    'GAMEOVER': self.game_over,
                    'MSG': self.display_msg}
        self.name = name
    
    def your_turn(self):
        self.game.last_set = self.game.other_player(self)
    
    def do_turn(self, turn):
        """ turn is (field, row, col, rot_dir, rot_field) """
        self.game.apply_turn(self, list(turn))
        
    def is_turn(self):
        """ Check whether it's the players turn. """
        return self.game.last_set is not self
    
    def display_turn(self, player, turn):
        """ Override to display turn when it is set to turn """
        pass
    
    def begin(self):
        pass
    
    def lookup(self, cmd):
        return self.cmd[cmd]
    
    def game_over(self, winner, loser):
        pass
    
    def quit_game(self):
        self.game.player_quit(self)
    
    def player_quit(self, opponent):
        pass
    
    def player_joined(self, player):
        pass
    
    def display_msg(self, author, msg):
        pass
    
    def send_msg(self, msg):
        self.game.send_msg(self.name, msg)
    
    def in_game(self):
        return self.game and self in self.game.players
    
    def serialize(self):
        return {'name': self.name}
    
    def __repr__(self):
        return "<Player %d>" % (self.uid)


class RemotePlayer(Player):
    def __init__(self, conn=None, name=None):
        Player.__init__(self, name)
        self.conn = conn
    
    def display_turn(self, player, turn):
        self.conn.send('GAME', [self.game.uid, 'TURN', turn])
    
    def display_msg(self, author, msg):
        self.conn.send('MSG', [self.game.uid, 'TURN', turn])


class Game(object):
    def __init__(self, board=None):
        """ If players are passed it automatically sets their game attribute 
        to this instance. """
        self.board = board or Board()
        self.players = []
        self.observers = []
        
        self.last_set = None
    
    def rules(self, turn):
        """ Checks that need to be done before player can set the stone. """
        quad, row, col, rot_dir, rot_field = turn
        if not 0 <= quad <= 3:
            raise InvalidTurn
        if not 0 <= row <= 2:
            raise InvalidTurn
        if not 0 <= col <= 2:
            raise InvalidTurn
        if not (rot_dir == CW or rot_dir == CCW):
            raise InvalidTurn
        if not 0 <= rot_field <= 3:
            raise InvalidTurn
        
    def apply_turn(self, player, turn):
        """ Apply turn of player to the board. Also checks whether it is the 
        players turn. 
        
        The other player's and all other observer's display_turn methods are
        called, it is the calling players responsibility to display it if
        needed! """
        self.rules(turn)
        if player is self.last_set:
            raise NotYourTurn
        
        self.board.apply_turn(player, turn)
        self.other_player(player).display_turn(player, turn)
        for obs in self.observers:
            obs.display_turn(player, turn)
        self.last_set = player
        winner, loser = self.get_winner()
        if winner is not None:
            for p in self.people():
                p.game_over(winner, loser)
    
    def get_winner(self):
        """ Return (winner, loser).
        
        If no winner has been found (None, None) is returned. """
        winner = self.board.win()
        if winner:
            return self.players[winner - 1], self.players[2 - winner]
        else:
            return None, None
    
    def new_id(self):
        players = len(self.players)
        if players == 2:
            raise GameFull
        return players + 1
    
    def add_player(self, p):
        # FIXME: Should we really get the ID here?
        if len(self.players) == 2:
            raise GameFull
        p.uid = self.new_id()
        p.game = self
        for person in self.people():
            person.player_joined(p)
        self.players.append(p)
    
    def add_player_with_uid(self, p):
        if len(self.players) == 2:
            raise GameFull
        p.game = self
        for person in self.people():
            person.player_joined(p)
        self.players.insert(p.uid - 1, p)
    
    def add_observer(self, o):
        self.observers.append(o)
    
    def random_beginner(self):
        """ Determine and return random beginner """
        self.last_set = random.choice(self.players)
        return self.other_player(self.last_set)
    
    def other_player(self, player):
        """ Get the player that is not player that is in the game """
        return self.players[2 - player.uid]
    
    def send_msg(self, author, msg):
        for p in self.people():
            p.display_msg(author, msg)
    
    def player_quit(self, player):
        if player not in self.players:
            raise ValueError
        
        self.players.remove(player)
        for p in self.people():
            p.player_quit(player)
    
    def people(self, but=None):
        for item in itertools.chain(self.players, self.observers):
            if item != but:
                yield item
