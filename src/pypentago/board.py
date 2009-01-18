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

import ctypes

NONE = 0
WHITE = 1
BLACK = 2


def _p_row(quad):
    return (quad >= 2)


def _p_col(quad):
    return (quad == 1 or quad == 3)



class BoardStruct(ctypes.Structure):
    _fields_ = [
        ("filled", ctypes.c_short),
        ("board",  ctypes.c_byte * 6 * 6),
        ("colour", ctypes.c_byte)
    ]


class Board:
    def __init__(self, beginner=1):
        self._struct = BoardStruct()
        for i in xrange(6):
            for j in xrange(6):
                self._struct.board[i][j] = 0
        self._struct.colour = beginner
        self.has_set = False
    
    def set_stone(self, quad, row, col):
        if self.has_set:
            raise ValueError
        self._struct.board[_p_row(quad) + row][_p_col(quad) + col] = (
            self._struct.colour)
        self._struct.colour = 3 - self._struct.colour

    def get_stone(self, quad, row, col):
        return self._struct[_p_row(quad) + row][_p_col(quad) + col]
    
    def rotate(self, quad, cw):
        row = 3 * _p_row(quad)
        col = 3 * _p_col(quad)
        q = [self._struct.board[row + r][col: col+3] for r in xrange(3)]

        for r in xrange(3):
            for c in xrange(3):
                if cw:
                    self._struct.board[row+c][col+2-r] = q[r][c]
                else:
                    self._struct.board[row+c][col+2-r] = q[2-r][2-c]

        self.has_set = False
    
    def rotate_cw(self, quad):
        self.rotate(quad, True)

    def rotate_ccw(self, quad):
        self.rotate(quad, False)
    
    def find_best(self, depth=4):
        raise NotImplementedError('Compile the goddamn C module.')
    
    def win(self):
        # TODO: Write me!
        raise NotImplementedError
    
    def do_best(self, depth=4):
        raise NotImplementedError('Compile the goddamn C module.')

    def __getitem__(self, i):
        return self._struct.board[i[0]][i[1]]
    
    def __setitem__(self, i, v):
        self._struct.board[i[0]][i[1]] = v

    def deallocate(self):
        pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.deallocate()

if __name__ == '__main__':
    b = Board()
    b.set_stone(0, 0, 0)
    b.rotate_ccw(0)
    b.set_stone(0, 0, 1)
    # b._print()
    print
    # b.do_best()
    # b._print()
    print b[2, 0]
    b[2, 0] = 2
    print b[2, 0]
    print b._struct.board[2][0]
    b._struct.board[2][0] = 1
    print b._struct.board[2][0]
    #b.do_best_turn()
    #b.do_best_turn()
    #board.print_board(b.ptr)
    #print ord(Board.from_address(b.ptr).colour)
    #b.do_best_turn()
    #print ord(Board.from_address(b.ptr).colour)

