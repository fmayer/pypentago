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


##########################################################
## About this file                                      ##
## ==================================================== ##
## This file is ongoing work of reimplementing the core ##
## of pypentago. It is currently not used at all, but   ##
## will be integrated into the pypentago project.       ##
## This will replace the pypentago.server.field module  ##
##########################################################


import sys
import os
import random

script_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(script_path, os.pardir)))

import depr

from pypentago import CW, CCW
from pypentago.exceptions import (InvalidTurn, SquareNotEmpty, NotYourTurn, 
                                  GameFull)


def has_won(line, check):
    """ Check whether line contains 5 stones of the same player. """
    if len(line) < 5:
        # Doesn't seem to be a full line
        return False
    return (list(line[0:5]) == list(check) or
            list(line[1:6]) == list(check))


def diagonal(inp, row, col):
    """ Return the two diagonals going down from the position
    (row, col) in inp """
    rows = len(inp)
    # Assume all rows have the same length!
    cols = len(inp[0])
    
    # List containing starting position
    coords = [[inp[row][col]]]
    x, y = row, col
    while x+1 < rows and y-1 >= 0:
        x, y = x+1, y-1
        coords[-1].append(inp[x][y])

    # List containing starting position
    coords.append([inp[row][col]])
    x, y = row, col
    while x+1 < rows and y+1 < cols:
        x, y = x+1, y+1
        coords[-1].append(inp[x][y])
    
    return coords
    
    
class Quadrant(object):
    def __init__(self, uid):
        self.uid = uid
        self.field = [
            [0, 0, 0], 
            [0, 0, 0],
            [0, 0, 0]
        ]
    
    def __repr__(self):
        return "<Quadrant(%s)>" % self.field
    
    def rotate_ccw(self):
        """ Rotate quadrant counter-clockwise. """
        newfield = [[self.field[k][i] for k in xrange(3)] for i in xrange(3)]
        # Reverse newfield.
        self.field[:] = newfield[::-1]
    
    def rotate_cw(self):
        """ Rotate quadrant clockwise. """
        newfield = [[self.field[2-k][2-i] for k in xrange(3)]
                    for i in xrange(3)]
        # Reverse newfield.
        self.field[:] = newfield[::-1]
    
    @depr.deprecated_alias(rotate_ccw)
    def rotleft(*args, **kwargs):
        pass
    
    @depr.deprecated_alias(rotate_cw)
    def rotright(*args, **kwargs):
        pass
        
    def rotate(self, clockwise):
        if clockwise:
            self.rotate_cw()
        else:
            self.rotate_ccw()

    def __getitem__(self, i):
        return self.field[i]

    def __setitem__(self, i, value):
        self.field[i] = value
    
    def checksum(self):
        return hash(tuple(map(tuple, self.field)))


class Board(object):
    """ The main pypentago board. 
    
    You can get the quadrants of it by getting items of the class. For instance
    board[0] gets you the upper left quadrant, board[1], the upper right 
    et cetera. 
    
    Please use the Game class for any real pypentago games as it offers a 
    more abstracted design and is better for interacting with the players. """
    def __init__(self):
        self.quadrants = [Quadrant(x) for x in xrange(4)]
    
    def __getitem__(self, i):
        return self.quadrants[i]
    
    def __setitem__(self, i, value):
        self.quadrants[i] = value

    def apply_turn(self, player, turn):
        """ Apply turn of player to board. 
        Turn is (quadrant, row, col, rot_dir, rot_field) """
        field, row, col, rot_dir, rot_field = turn
        self.set_stone(player, field, row, col)
        if rot_dir == CW:
            self[rot_field].rotate_cw()
        elif rot_dir == CCW:
            self[rot_field].rotate_ccw()
        else:
            self[field][row][col] = 0
            raise InvalidTurn
        
    def set_stone(self, player, field, row, col):
        """
        Sets a stone of player.
        """
        if not self[field][row][col]:
            self[field][row][col] = player.uid
        else:
            raise SquareNotEmpty(
                  "Cannot set stone at quadrant %s row %s col %s" %
                  (field, row, col))
    
    def get_row(self, row):
        """ Get the row'th row starting from the top. """
        field = 0
        if row > 2:
            field = 2
            row = row - 3
        return (list(self[field][row]) +
                list(self[field+1][row]))
    
    def get_col(self, col):
        """ Get the col'th row starting from the left. """
        return self.cols[col]
    
    def get_diagonal(self, row, col):
        """ Get diagonals starting from the point (row, col) """
        return diagonal(self.rows, row, col)
    
    @property
    def diagonals(self):
        """ Get all diagonals of the board """
        r = []
        for x in xrange(6):
            for y in xrange(6):
                r.extend(self.get_diagonal(x, y))
        return r
    
    @property
    def rows(self):
        """ Get all rows of the board """
        return [self.get_row(elem) for elem in xrange(6)]
    
    @property
    def cols(self):
        """ Get all colums of the board """
        return zip(*self.rows)

    def __str__(self):
        string = ""
        for i, row in enumerate(self.rows):
            r = map(str, row)
            string+='%s  %s\n' % (' '.join(r[:3]), ' '.join(r[3:]))
            if i == 2:
                string+="\n"
        return string
    
    def checksum(self):
        return hash(tuple(q.checksum() for q in self.quadrants))

        
class Player(object):
    """ The Player is the one that is interacting with the Game. """
    def __init__(self):
        self.game = None
        self.uid = None
        self.cmd = {'TURN': self.do_turn,
                    'GAMEOVER': self.game_over,
                    'MSG': self.display_msg}
    
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
    
    def game_over(self, winner):
        pass
    
    def quit_game(self):
        self.game.player_quit(self)
    
    def opponent_quit(self, opponent):
        pass
    
    def display_msg(self, author, msg):
        pass
    
    def send_msg(self, msg):
        self.game.send_msg(self.name, msg)
    
    def __repr__(self):
        return "<Player %d>" % (self.uid)
    
    @property
    def name(self):
        return "Player %d" % self.uid


class RemotePlayer(Player):
    def __init__(self, conn=None):
        Player.__init__(self)
        self.cmd.update({'LOCALTURN': self.local_turn})
        self.conn = conn
    
    def local_turn(self):
        self.game.last_set = self
    
    def display_turn(self, player, turn):
        self.conn.send('GAME', [self.game.uid, 'TURN', turn])


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
            winner.game_over(True)
            loser.game_over(False)
    
    def get_winner(self):
        """ Return (winner, loser).
        
        If no winner has been found (None, None) is returned. """
        for player in self.players:           
            check = [player.uid]*5
            for line in (self.board.cols + self.board.rows + 
                         self.board.diagonals):
                if has_won(line, check):
                    return player, self.other_player(player)
        return None, None
    
    def new_id(self):
        players = len(self.players)
        if players == 2:
            raise GameFull
        return players + 1
    
    def add_player(self, p):
        if len(self.players) == 2:
            raise GameFull
        p.uid = self.new_id()
        p.game = self
        self.players.append(p)
    
    def random_beginner(self):
        """ Determine and return random beginner """
        self.last_set = random.choice(self.players)
        return self.other_player(self.last_set)
    
    def other_player(self, player):
        """ Get the player that is not player that is in the game """
        return self.players[2 - player.uid]
    
    def checksum(self):
        return self.board.checksum()
    
    def send_msg(self, author, msg):
        for p in self.players:
            p.display_msg(author, msg)
    
    def player_quit(self, player):
        if player not in self.players:
            raise ValueError
        
        self.players.remove(player)
        for p in self.players:
            p.opponent_quit(player)
