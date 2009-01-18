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
import os

import pypentago


board = ctypes.CDLL(os.path.join(pypentago.LIB_PATH, 'board.so'))


NONE = 0
WHITE = 1
BLACK = 2


class Turn(ctypes.Structure):
    _fields_ = [
        ('row', ctypes.c_ubyte),
        ('col', ctypes.c_ubyte),
        ('quad', ctypes.c_ubyte),
        ('dir', ctypes.c_ubyte),
        ('value', ctypes.c_float)
    ]
    
    def __repr__(self):
        return "<Turn (%d, %d, %d, %s, %f)>" % (self.row, self.col,
                                                self.quad, ord(self.dir),
                                                self.value)


class BoardStruct(ctypes.Structure):
    _fields_ = [
        ("filled", ctypes.c_byte),
        ("board",  ctypes.c_byte * 6 * 6),
        ("colour", ctypes.c_byte)
    ]


class Board:
    def __init__(self, beginner=1):
        self._ptr = board.new_board(beginner)
        self._allocated = True
        self._struct = BoardStruct.from_address(self._ptr)
        self.has_set = False
    
    def set_stone(self, quad, row, col):
        if self.has_set:
            raise ValueError
        board.set_stone(self._ptr, quad, row, col)
        self.has_set = True

    def get_stone(self, quad, row, col):
        return board.get_stone(self._ptr, quad, row, col)
    
    def rotate_cw(self, quad):
        board.rotate_cw(self._ptr, quad)
        self.has_set = False
    
    def rotate_ccw(self, quad):
        board.rotate_ccw(self._ptr, quad)
        self.has_set = False
    
    def find_best(self, depth=4):
        t = board.find_best(self._ptr, depth)
        return Turn.from_address(t)
    
    def win(self):
        return board.won(self._ptr)
    
    def do_best(self, depth=4):
        t = board.find_best(self._ptr, depth)
        board.do_turn(self._ptr, t)
        board.free_turn(t)

    def __getitem__(self, i):
        return self._struct.board[i[0]][i[1]]
    
    def __setitem__(self, i, v):
        self._struct.board[i[0]][i[1]] = v
    
    def _print(self):
        board.print_board(self._ptr)

    def deallocate(self):
        board.free_board(self._ptr)
        self._allocated = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        self.deallocate()


if __name__ == '__main__':
    b = Board()
    b.set_stone(0, 0, 0)
    b.rotate_ccw(0)
    b.set_stone(0, 0, 1)
    b._print()
    print
    b.do_best()
    b._print()
    print b[2, 0]
    b[2, 0] = 2
    for x in xrange(6):
        for y in xrange(6):
            print b[x, y], '=', b._struct.board[x][y]
    b._struct.board[2][0] = 1
    print b._struct.board[2][0]
    #b.do_best_turn()
    #b.do_best_turn()
    #board.print_board(b.ptr)
    #print ord(Board.from_address(b.ptr).colour)
    #b.do_best_turn()
    #print ord(Board.from_address(b.ptr).colour)
    
