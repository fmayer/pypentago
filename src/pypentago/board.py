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

import itertools

import pypentago
import pypentago.util

from pypentago.exceptions import SquareNotEmpty

NONE = 0
WHITE = 1
BLACK = 2


def has_won(line, check):
    """ Check whether line contains 5 stones of the same player. """
    i = 0
    j = 0
    for elem in line:
        if elem == check:
            i += 1
            if i >= 5:
                return True
        else:
            i = 0
            j += 1
            if j >= 2:
                return False
    return False


class Board(object):
    """
    Direct access to underlying data structure can be done using tuples
    as indices on the board object. This doesn't increase the filled
    member when a new stone is set, nor does it raise an exception
    if the square has not been empty.
    
        >>> board = Board()
        >>> board[1, 0] = 1
        >>> board[1, 0]
        1
        >>> board.filled
        0
    
    More high-level access is provided via the get and set methods. They
    increase the counter and raise pypentago.exceptions.SquareNotEmpty if
    the square you attempted to set a stone to is already taken by another
    one.
    
        >>> board = Board()
        >>> board.set(1, 0, 1)
        >>> board.get(1, 0)
        1
        >>> board.filled
        1
        >>> board.set(1, 0, 1) # doctest: +ELLIPSIS
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File ".../pypentago/board.py", line 90, in set
            raise SquareNotEmpty
        pypentago.exceptions.SquareNotEmpty
        >>> 
    
    You can get a string representation of the board for debug purposes 
    using the str builtin.
    
        >>> print str(board)
        0 0 0  0 0 0
        1 0 0  0 0 0
        0 0 0  0 0 0
        
        0 0 0  0 0 0
        0 0 0  0 0 0
        0 0 0  0 0 0
        >>> 

    """
    def __init__(self, beginner=1):
        self.board = [[0 for _ in xrange(6)] for _ in xrange(6)]
        self.filled = 0
    
    def apply_turn(self, playerid, turn):
        """ turn is (quad, row, col, rot_dir, rot_quad). """
        quad, row, col, rot_dir, rot_quad = turn
        self.set_relative(quad, row, col, playerid)
        if rot_dir == pypentago.CW:
            self.rotate_cw(rot_quad)
        elif rot_dir == pypentago.CCW:
            self.rotate_ccw(rot_quad)
        else:
            raise ValueError
    
    def set(self, row, col, value):
        """ Set square at absolute position row, col to value. If the square
        isn't empty, raise pypentago.exceptions.SquareNotEmpty.
        
        Increase the filled counter by one. """
        if self.board[row][col]:
            raise SquareNotEmpty
        self.board[row][col] = value
        if value:
            self.filled += 1
    
    def get(self, row, col):
        """ Get value of square at absolute position row, col. """
        return self.board[row][col]
    
    def set_relative(self, quad, row, col, value):
        """ Set value of square with row, col coordinates relative
        to quadrant quad. """
        arow, acol = pypentago.util.absolute(quad, row, col)
        self.set(arow, acol, value)
    
    def get_relative(self, quad, row, col):
        """ Get value of square with row, col coordinates relative
        to quadrant quad. """
        arow, acol = pypentago.util.absolute(quad, row, col)
        return self.board[arow][acol]
    
    def rotate(self, quad, cw):
        """ Rotate the quadrant quad clockwise if cw equals True
        or counter-clockwise otherwise. """
        if quad < 0 or quad > 3:
            # This wouldn't go well.
            raise ValueError
        
        b = self.board
        row, col = pypentago.util.offset(quad)
        q = [b[row + r][col: col+3] for r in xrange(3)]
        
        for r in xrange(3):
            for c in xrange(3):
                if cw:
                    b[row+c][col+2-r] = q[r][c]
                else:
                    b[row+c][col+2-r] = q[2-r][2-c]
    
    def rotate_cw(self, quad):
        """ Rotate the quadrant quad clockwise. """
        self.rotate(quad, True)
    
    def rotate_ccw(self, quad):
        """ Rotate the quadrant quad counter-clockwise. """
        self.rotate(quad, False)
    
    def win(self):
        """ If a winner has been found, return their id. If the game is
        a draw, return 3. If no winner has been found return 0. """
        if self.filled == 36:
            return 3
        winner = 0
        for player in (1, 2):           
            for line in itertools.chain(self.cols, self.rows,
                                        self.diagonals):
                if has_won(line, player):
                    if not winner:
                        winner = player
                    elif winner != player:
                        return 3
        return winner
    
    def get_row(self, row):
        for i in xrange(6):
            yield self.board[row][i]
    
    def get_col(self, col):
        for i in xrange(6):
            yield self.board[i][col]
    
    def get_dia_downwards(self, r, c):
        for x in xrange(6 - (r or c)):
            yield self.board[r+x][c+x]
    
    def get_dia_upwards(self, r, c):
        for x in xrange(6 - (r or c)):
            yield self.board[r+x][5-(c+x)]
    
    @property
    def diagonals(self):
        yield self.get_dia_downwards(0, 0)
        yield self.get_dia_downwards(0, 1)
        yield self.get_dia_downwards(1, 0)
        yield self.get_dia_upwards(0, 0)
        yield self.get_dia_upwards(0, 1)
        yield self.get_dia_upwards(1, 0)
    
    @property
    def rows(self):
        return (self.get_row(i) for i in xrange(6))
    
    @property
    def cols(self):
        return (self.get_col(i) for i in xrange(6))
    
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
