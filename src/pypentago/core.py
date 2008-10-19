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


##########################################
## TODO:                                 #
## Communication between Game and Player #
## Make sys.path modification redundant  #
##########################################


import sys
import os
import random

script_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(os.path.join(script_path, os.pardir)))

from pypentago.exceptions import (InvalidTurn, SquareNotEmpty, NotYourTurn, 
                                  GameFull)

def has_won(line, check):
    """ Check whether line contains 5 stones of the same player. """
    return list(line[0:5]) == list(check) or \
           list(line[1:6]) == list(check)


def diagonal(inp, line, col):
    """ Get diagonals in both directions downwards starting at (line, col) """
    # This function is ugly. Nothing to see here. Go on!
    a, b, c, d = [], [], [], []
    # Get diagonal going down to the right
    x = 0
    while line+x < len(inp) and col+x < len(inp[0]):
        a.append(inp[line+x][col+x])
        x+=1
    # Get diagonal going down to the left
    x = 0
    while x >= 0 and col-x >= 0:
        b.append(inp[line-x][col-x])
        x+=1
    x = 0
    while line+x < len(inp) and col-x >= 0:
        c.append(inp[line+x][col-x])
        x+=1
    x = 0
    while col+x < len(inp) and line-x >= 0:
        d.append(inp[line-x][col+x])
        x+=1
    return [a] + [b] + [c] + [d]
    
    
class Quadrant:
    def __init__(self, uid):
        self.uid = uid
        self.field = [
            [0, 0, 0], 
            [0, 0, 0],
            [0, 0, 0]
        ]
    
    def __repr__(self):
        return "<Quadrant(%s)>" % self.field
    
    def rotleft(self):
        """ Rotate quadrant to the left. """
        newfield = []
        for i in xrange(3):
            newfield.append([])
            for k in xrange(3):
                newfield[i].append(self.field[k][i])
        self.field = list(reversed(newfield))
    
    def rotright(self):
        """ Rotate quadrant to the right. """
        newfield = []
        for i in xrange(3):
            newfield.append([])
            for k in xrange(3):
                newfield[i].append(self.field[2-k][2-i])
        self.field = list(reversed(newfield))

    def __getitem__(self, i):
        return self.field[i]

    def __setitem__(self, i, value):
        self.field[i] = value


class Board:
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
        Turn is (field, row, col, rot_dir, rot_field) """
        field, row, col, rot_dir, rot_field = turn
        self.set_stone(player, field, row, col)
        if rot_dir == "R":
            self[rot_field].rotright()
        elif rot_dir == "L":
            self[rot_field].rotleft()
        else:
            raise InvalidTurn
        
    def set_stone(self, player, field, row, col):
        """
        Sets a stone of player.
        """
        if not self[field][row][col]:
            self[field][row][col] = player.uid
        else:
            raise SquareNotEmpty(
                  "Cannot set stone at quadrant %s row %s col %s" % \
                  (field, row, col))
    
    def get_row(self, row):
        """ Get the row'th row starting from the top. """
        field = 0
        if row > 2:
            field = 2
            row = row - 3
        return list(self[field][row]) + \
               list(self[field+1][row])
    
    def get_col(self, col):
        """ Get the col'th row starting from the left. """
        return self.cols[col]
    
    def get_diagonal(self, row, col):
        """ Get diagonals starting from the point (row, col) """
        return diagonal(self.rows, row, col)
    
    @property
    def diagonals(self):
        """ Get all diagonals of the board """
        # "[winner_id] * 5 in diagonals" to get winner!
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
            string+="%s %s %s  %s %s %s\n" % (row[0], row[1],
                                              row[2], row[3],
                                              row[4], row[5])
            if i == 2:
                string+="\n"
        return string


class Game:
    def __init__(self, players=None):
        """ If players are passed it automatically sets their game attribute 
        to this instance. """
        self.board = Board()
        self.next_uid = 1
        self.players = players
        self.observers = []
        for i, player in enumerate(players):
            player.game = self
            player.uid = i+1
        self.last_set = None
    
    def rules(self, turn):
        """ Checks that need to be done before player can set the stone. """
        field, row, col, rot_dir, rot_field = turn
        if not row in xrange(3):
            raise InvalidTurn
        if not col in xrange(3):
            raise InvalidTurn
        if not rot_dir in ("L", "R"):
            raise InvalidTurn
        if not rot_field in xrange(4):
            raise InvalidTurn
        
    def apply_turn(self, player, turn):
        """ Apply turn of player to the board. Also checks whether it is the 
        players turn. """
        self.rules(turn)
        if player is self.last_set:
            raise NotYourTurn
        
        self.board.apply_turn(player, turn)
        for a_player in self.players:
            a_player.display_turn(player, turn)
        self.last_set = player
    
    def get_winner(self):
        """ Either return False if no-one has won or a tuple (winner, loser). 
        """
        for player in self.players:
            pl = list(self.players[:])
            pl.remove(player)
            other_player = pl[0]
            
            check = [player.uid]*5
            for line in self.board.cols + self.board.rows:
                if has_won(line, check):
                    return player, other_player
            if check in self.board.diagonals:
                return player, other_player
        return False
    
    def add_player(self, player):
        """ Add player to the game. Sets the uid and game attributes of player.
        
        Raises GameFull exception if game is full. """
        if len(self.players) < 2:
            self.players.append(player)
            player.game = self
            player.uid = self.next_uid
            self.next_uid+=1
        else:
            raise GameFull
    
    def get_random_beginner(self):
        self.last_set = random.choice(self.players)

        
class Player:
    """ The Player is the one that is interacting with the Game. """
    def __init__(self, game=None, uid=None):
        self.game = game
        self.uid = uid
    
    def do_turn(self, turn):
        """ turn is (field, row, col, rot_dir, rot_field) """
        self.game.apply_turn(self, list(turn))
        
    def is_turn(self):
        """ Check whether it's the players turn. """
        return self.game.last_set is not self
    
    def display_turn(self, player, turn):
        """ Override to display turn when it is set to turn """
        pass

        
import unittest

class TestGame(unittest.TestCase):
    def test_win_dia(self):
        game = Game((Player(), Player()))
        board = game.board
        # Construct winning situation.
        board[0][0][0] = 2
        board[0][1][1] = 2
        board[0][2][2] = 2
        board[3][0][0] = 2
        board[3][1][1] = 2

        # See whether the winner has been found.
        winner = game.get_winner()
        self.assertNotEqual(winner, False)
        self.assertEqual(winner[0].uid, 2)

    def test_win_dia_sec(self):
        game = Game((Player(), Player()))
        board = game.board
        # Construct winning situation.
        board[0][0][1] = 2
        board[0][1][2] = 2
        board[1][2][0] = 2
        board[3][0][1] = 2
        board[3][1][2] = 2

        # See whether the winner has been found.
        winner = game.get_winner()
        self.assertNotEqual(winner, False)
        self.assertEqual(winner[0].uid, 2)

    def test_square_not_empty(self):
        game = Game((Player(), Player()))
        game.apply_turn(game.players[0], (0, 0, 0, "R", 1))
        self.assertRaises(SquareNotEmpty, game.apply_turn, 
                          game.players[1], (0, 0, 0, "R", 1))


if __name__ == "__main__":
    unittest.main()        