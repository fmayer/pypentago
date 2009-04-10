# -*- coding: us-ascii -*-

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

import pypentago.util

from pypentago import CW, CCW, rpcializer
from pypentago.exceptions import (InvalidTurn, SquareNotEmpty, NotYourTurn, 
                                  GameFull, GameOver)


try:
    # The extension module is critically bugged.
    raise ImportError
    from pypentago._board import Board
    EXTENSION_MODULE = True
except ImportError:
    from pypentago.board import Board
    EXTENSION_MODULE = False


draw = object()


class Turn(rpcializer.TrivialClass):
    def __init__(self, row, col, rot_dir, rot_quad):
        self.row = row
        self.col = col
        self.rot_quad = rot_quad
        self.rot_dir = rot_dir
    
    def __iter__(self):
        return iter((self.row, self.col, self.rot_quad, self.rot_dir))
    
    def relative_position(self):
        """ (quadrant, relative_row, relative_col) """
        quad = pypentago.util.contains(self.row, self.col)
        rows, cols = pypentago.util.offset(quad)
        return quad, self.row - rows, self.col - cols


class Observer(object):
    def display_turn(self, turn):
        pass
    
    def game_over(self, winner, loser):
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
        self.name = name
    
    def do_turn(self, turn):
        """ turn is (field, row, col, rot_dir, rot_field) """
        self.game.apply_turn(self, list(turn))
        
    def is_turn(self):
        """ Check whether it's the players turn. """
        return self.game.last_set is not self
    
    def display_turn(self, player, turn):
        """ Override to display turn when it is set to turn """
        pass
    
    def game_over(self, winner, loser):
        """ Called when the game is over. """
        pass
    
    def quit_game(self):
        """ Remove the player from their game. """
        self.game.player_quit(self)
        # FIXME: Should we do this?
        self.game = None
    
    def player_quit(self, opponent):
        """ Called when the opponent quits the game. """
        pass
    
    def player_joined(self, player):
        """ Call when another player joins the game. """
        pass
    
    def display_msg(self, author, msg):
        """ Called when a message is sent in the game. """
        pass
    
    def send_msg(self, msg):
        """ Send a message to the game. The other player's display_msg
        is called by the game. """
        if msg.strip():
            self.game.send_msg(self, msg)
    
    def in_game(self):
        """ Return True if the player is in a game. """
        return self.game and self in self.game.players
    
    def serialize(self):
        """ Return dictionary with the information about the player. """
        return {'name': self.name}
    
    def __repr__(self):
        return "<Player %d>" % (self.uid)


class RemotePlayer(Player):
    """ The RemotePlayer sends everything he observes trough
    the connection passed to it. """
    def __init__(self, conn=None, name=None):
        Player.__init__(self, name)
        self.cmd = {
                'TURN': self.do_turn,
                'GAMEOVER': self.game_over,
                'MSG': self.send_msg,
                'QUIT': self.quit_game,
        }
        self.conn = conn
    
    def lookup(self, cmd):
        return self.cmd[cmd]
    
    def display_turn(self, player, turn):
        self.conn.send(
            *rpcializer.game(self.game, 'TURN', rpcializer.raw(turn))
        )
    
    def display_msg(self, author, msg):
        self.conn.send(
            *rpcializer.game(self.game, 'MSG', rpcializer.raw(msg))
        )
    
    def player_quit(self, player):
        self.conn.send(
            *rpcializer.game(self.game, 'QUIT')
        )
    
    def quit_game(self):
        del self.conn.remote_table[self.game.uid]
        
        # Prevent the games from being synced twice.
        a = len(self.game.players) == 2

        Player.quit_game(self)
        if a and hasattr(self.conn, 'server'):
            self.conn.server.sync_games()


class Game(object):
    def __init__(self, board=None):
        self.board = board or Board()
        self.players = []
        self.observers = []
        self.over = False
        
        self.rpcialize_table = {
            '': lambda x: x,
            'player_by_id': self.player_by_id,
        }
        
        self.last_set = None
    
    def player_by_id(self, uid):
        """ Get played with the uid in the game. """
        return self.players[uid - 1]
    
    def unrpcialize(self, args):
        for arg in args:
            e, d = arg
            yield self.rpcialize_table[e](d)
    
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
        if self.over:
            raise GameOver
        
        self.rules(turn)
        if player is self.last_set:
            raise NotYourTurn
        
        self.board.apply_turn(player, turn)
        self.last_set = player
        
        for person in self.people(player):
            person.display_turn(player, turn)
        
        winner, loser = self.get_winner()
        if winner is not None:
            self.game_over(winner, loser)
            for p in self.people():
                p.game_over(winner, loser)
    
    def get_winner(self):
        """ Return (winner, loser).
        
        If no winner has been found (None, None) is returned. """
        winners = self.board.win()
        if len(winners) == 1:
            winner = self.player_by_id(winners[0])
            return winner, self.other_player(winner)
        elif len(winners) == 2:
            return draw, draw
        else:
            return None, None
    
    def new_id(self):
        """ Get the next free uid for a player. """
        players = len(self.players)
        if players == 2:
            raise GameFull
        return players + 1
    
    def add_player(self, p):
        """ Add player. The next free uid is used. The player's uid
        member is set to the uid. If the game is already full, raise
        pypentago.exceptions.GameFull.
        
        This will call the player_joined method of all people in the game,
        except the one that just joined. """
        # FIXME: Should we really get the ID here?
        if len(self.players) == 2:
            raise GameFull
        p.uid = self.new_id()
        p.game = self
        for person in self.people():
            person.player_joined(p)
        self.players.append(p)
    
    def add_player_with_uid(self, p):
        """ Add player that has a uid member. It will be added to the
        game with this id. If a player with the same uid already is in
        the game, raise ValueError. If the game is already full, raise
        pypentago.exceptions.GameFull.
        
        This will call the player_joined method of all people in the game,
        except the one that just joined. """
        if len(self.players) == 2:
            raise GameFull
        
        for player in self.players:
            if player == p.uid:
                raise ValueError("Duplicate uid in game!")
        
        p.game = self
        for person in self.people():
            person.player_joined(p)
        self.players.insert(p.uid - 1, p)
    
    def add_observer(self, o):
        """ Add observer to the game. """
        # TODO: Make observers work.
        self.observers.append(o)
    
    def random_beginner(self):
        """ Determine and return random beginner """
        self.last_set = random.choice(self.players)
        return self.other_player(self.last_set)
    
    def other_player(self, player):
        """ Get the player that is not player that is in the game """
        return self.players[2 - player.uid]
    
    def send_msg(self, author, msg):
        """ Send message to the game. It is the callers responsibility
        to display it. The author's display_msg isn't called. """
        for p in self.people(author):
            p.display_msg(author.name, msg)
    
    def player_quit(self, player):
        """ Remove player from the game. The game is over afterwards. """
        if player not in self.players:
            raise ValueError
        
        self.over = True
        
        self.players.remove(player)
        for p in self.people():
            # FIXME: Also call p.game_over?
            p.player_quit(player)
    
    # FIXME: Rename to attendees?
    def people(self, but=None):
        """ Yield all people in the game. If optional but is used, exclude
        everything that equals it. This is useful if we do not want to call
        a method of the caller.
        
        All objects yielded by this should at least have the Observer interface
        implemented (display_turn, game_over, display_msg, player_quit,
        player_joined). """
        for item in itertools.chain(self.players, self.observers):
            if item != but:
                yield item
    
    def game_over(self, winner, loser):
        self.over = True
        
