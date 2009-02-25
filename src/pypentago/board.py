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

""" Pure Python implementation of the pypentago board.
Only basic checks, like preventing setting a stone on a square that is not
empty are done. It does make no attempts of managing the players in any way.
This is the responsibility of pypentago.core.Game.

For an optimized C implementation see pypentago._board. """

import ctypes
import pypentago
import itertools
from pypentago.exceptions import SquareNotEmpty

NONE = 0
WHITE = 1
BLACK = 2


def has_won(line, check):
    """ Check whether line contains 5 stones of the same player. """
    if len(line) < 5:
        # Doesn't seem to be a full line
        return False
    if len(line) == 6:
        return (list(line[0:5]) == list(check) or
                list(line[1:6]) == list(check))
    else:
        return list(line[0:5]) == list(check)


def _p_row(quad):
    return (quad >= 2)


def _p_col(quad):
    return (quad == 1 or quad == 3)


class Board:
    def __init__(self, beginner=1):
        self.board = [[0 for _ in xrange(6)] for _ in xrange(6)]
        self.filled = 0
        self.colour = 0
        for i in xrange(6):
            for j in xrange(6):
                self.board[i][j] = 0
        self.colour = beginner
    
    def apply_turn(self, player, turn):
        quad, row, col, rot_dir, rot_quad = turn
        self.set_stone(player, quad, row, col)
        if rot_dir == pypentago.CW:
            self.rotate_cw(rot_quad)
        elif rot_dir == pypentago.CCW:
            self.rotate_ccw(rot_quad)
        else:
            raise ValueError
    
    def set_stone(self, player, quad, row, col):
        if self.get_pos(quad, row, col):
            raise SquareNotEmpty
        self.set_pos(quad, row, col, player.uid)
    
    def set_pos(self, quad, row, col, value):
        self.board[3*_p_row(quad) + row][3*_p_col(quad) + col] = value

    def get_pos(self, quad, row, col):
        return self.board[3*_p_row(quad) + row][3*_p_col(quad) + col]
    
    def get_row(self, row):
        for i in xrange(6):
            yield self.board[row][i]
    
    def get_col(self, col):
        for i in xrange(6):
            yield self.board[i][col]
    
    def get_dia(self, r, c):
        for x in xrange(6 - (r or c)):
            yield self.board[r+x][c+x]
    
    @property
    def diagonals(self):
        yield self.get_dia(0, 0)
        yield self.get_dia(0, 1)
        yield self.get_dia(1, 0)
    
    @property
    def rows(self):
        return (self.get_row(i) for i in xrange(6))
    
    @property
    def cols(self):
        return (self.get_col(i) for i in xrange(6))
    
    def rotate(self, quad, cw):
        b = self.board
        row = 3 * _p_row(quad)
        col = 3 * _p_col(quad)
        q = [b[row + r][col: col+3] for r in xrange(3)]

        for r in xrange(3):
            for c in xrange(3):
                if cw:
                    b[row+c][col+2-r] = q[r][c]
                else:
                    b[row+c][col+2-r] = q[2-r][2-c]
    
    def rotate_cw(self, quad):
        self.rotate(quad, True)

    def rotate_ccw(self, quad):
        self.rotate(quad, False)
    
    def find_best(self, player, depth=4):
        raise NotImplementedError('Compile the goddamn C module.')
    
    def do_best(self, player, depth=4):
        raise NotImplementedError('Compile the goddamn C module.')
    
    def win(self):
        for player in (1, 2):           
            check = [player]*5
            for line in itertools.chain(self.cols, self.rows,
                                        self.diagonals):
                if has_won(list(line), check):
                    return player
        return 0
    
    def __str__(self):
        ret = []
        for i, row in enumerate(map(list, self.rows)):
            first = ' '.join(map(str, row[:3]))
            second = ' '.join(map(str, row[3:]))
            ret.append(first + '  ' + second)
            if i == 2:
                ret.append('')
        return '\n'.join(ret)
    
    def __setitem__(self, i, v):
        r, c = i
        self.board[r][c] = v
    
    def __getitem__(self, i):
        r, c = i
        return self.board[r][c]
