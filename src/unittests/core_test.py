#! /usr/bin/env python
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


import unittest
import itertools

import pypentago.util

from pypentago import core
from pypentago import board
from pypentago.exceptions import (SquareNotEmpty, NotYourTurn, GameFull,
                                  InvalidTurn)

def diagonal_up(x, y, p):
    def test(self):
        board = self.game.board
        board[0 + x, 0 + y] = p
        board[1 + x, 1 + y] = p
        board[2 + x, 2 + y] = p
        board[3 + x, 3 + y] = p
        board[4 + x, 4 + y] = p
        winner, loser = self.game.get_winner()
        self.assertNotEqual(winner, None)
        self.assertEqual(winner.uid, p)
    return test


def diagonal_down(x, y, p):
    def test(self):
        board = self.game.board
        board[0 + x, 5 - y] = p
        board[1 + x, 4 - y] = p
        board[2 + x, 3 - y] = p
        board[3 + x, 2 - y] = p
        board[4 + x, 1 - y] = p
        winner, loser = self.game.get_winner()
        self.assertNotEqual(winner, None)
        self.assertEqual(winner.uid, p)
    return test

class Called(Exception):
    pass
def fail(*args, **kw):
    raise Called

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = core.Game()
        self.players = [core.Player() for _ in xrange(2)]
        for p in self.players:
            self.game.add_player(p)
    
    test_upper_downwards_dia_p1 = diagonal_down(0, 1, 1)
    test_upper_downwards_dia_p2 = diagonal_down(0, 1, 2)
    test_uppermiddle_downwards_dia_p1 = diagonal_down(0, 0, 1)
    test_uppermiddle_downwards_dia_p2 = diagonal_down(0, 0, 2)
    test_lowermiddle_downwards_dia_p1 = diagonal_down(1, 1, 1)
    test_lowermiddle_downwards_dia_p2 = diagonal_down(1, 1, 2)
    test_lower_downwards_dia_p1 = diagonal_down(1, 0, 1)
    test_lower_downwards_dia_p2 = diagonal_down(1, 0, 2)

    test_upper_upwards_dia_p1 = diagonal_up(0, 1, 1)
    test_upper_upwards_dia_p2 = diagonal_up(0, 1, 2)
    test_uppermiddle_upwards_dia_p1 = diagonal_up(0, 0, 1)
    test_uppermiddle_upwards_dia_p2 = diagonal_up(0, 0, 2)
    test_lowermiddle_upwards_dia_p1 = diagonal_up(1, 1, 1)
    test_lowermiddle_upwards_dia_p2 = diagonal_up(1, 1, 2)
    test_lower_upwards_dia_p1 = diagonal_up(1, 0, 1)
    test_lower_upwards_dia_p2 = diagonal_up(1, 0, 2)
    
    def test_boardfull(self):
        self.game.board.filled = 36
        
        winner, loser = self.game.get_winner()
        self.assertEqual(winner, core.draw)
    
    def test_draw(self):
        board = self.game.board
        for i in xrange(5):
            board[0, i] = 1
        for i in xrange(5):
            board[1, i] = 2
        
        winner, loser = self.game.get_winner()
        self.assertEqual(winner, core.draw)
    
    def test_rotate_cw(self):
        board = self.game.board
        board[0, 0] = 1
        board.rotate_cw(0)
        self.assertEquals(board[0, 2], 1)
        
        board[0, 3] = 2
        board.rotate_cw(1)
        self.assertEquals(board[0, 5], 2)

    def test_rotate_ccw(self):
        board = self.game.board
        board[0, 2] = 1
        board.rotate_ccw(0)
        self.assertEquals(board[0, 0], 1)
        
        board[0, 5] = 2
        board.rotate_ccw(1)
        self.assertEquals(board[0, 3], 2)
    
    def test_win_row(self, p=1):
        for row in xrange(6):
            for x in xrange(2):
                # reset board
                self.setUp()
                b = self.game.board
                for col in xrange(5):
                    b[row, col + x] = p
                winner, loser = self.game.get_winner()
                self.assertNotEqual(winner, None)
                self.assertEqual(winner.uid, p)
    
    def test_win_row_p2(self):
        self.test_win_row(2)
    
    def test_win_col(self, p=1):
        for col in xrange(6):
            for x in xrange(2):
                # reset board
                self.setUp()
                b = self.game.board
                for row in xrange(5):
                    b[row + x, col] = p
                winner, loser = self.game.get_winner()
                self.assertNotEqual(winner, None)
                self.assertEqual(winner.uid, p)
    
    def test_win_col_p2(self):
        self.test_win_col(2)

    def test_square_not_empty(self):
        self.players[0].do_turn((0, 0, 0, "R", 1))
        self.assertRaises(SquareNotEmpty, self.players[1].do_turn, 
                          (0, 0, 0, "R", 1))
    
    def test_not_your_turn(self):
        self.players[0].do_turn((0, 0, 0, "R", 1))
        self.assertRaises(NotYourTurn, self.players[0].do_turn, 
                          (1, 0, 0, "R", 1))
    
    def test_game_full(self):
        self.assertRaises(GameFull, self.game.new_id)
    
    def test_players(self):
        p_1, p_2 = self.players
        p_2.display_turn = fail
        # See if p_2.display_turn gets called
        self.assertRaises(Called, p_1.do_turn, (1, 0, 0, "R", 1))
    
    def test_beginner(self):
        beginner = self.game.random_beginner()
        other = self.game.other_player(beginner)
        self.assertRaises(NotYourTurn, other.do_turn, (1, 0, 0, "R", 1))
        self.assertEqual(beginner.do_turn((1, 0, 0, "R", 1)), None)
    
    def test_other(self):
        one, other = self.players
        self.assert_(self.game.other_player(one) is other)
        self.assert_(self.game.other_player(other) is one)
    
    def test_invalid(self):
        p_1, p_2 = self.players
        self.assertRaises(InvalidTurn, p_1.do_turn, (42, 0, 0, "R", 1))
        self.assertRaises(InvalidTurn, p_1.do_turn, (0, 42, 0, "R", 1))
        self.assertRaises(InvalidTurn, p_1.do_turn, (0, 0, 42, "R", 1))
        self.assertRaises(InvalidTurn, p_1.do_turn, (0, 0, 0, "cake", 1))
        self.assertRaises(InvalidTurn, p_1.do_turn, (0, 0, 0, "R", 5))
    
    def test_quit(self):
        p_1, p_2 = self.players
        p_2.player_quit = fail
        self.assertRaises(Called, p_1.quit_game)
    
    def test_no_win(self):
        board = self.game.board
        board[0, 0] = 1
        board[0, 1] = 1
        board[0, 2] = 1
        board[0, 3] = 1
        board[0, 5] = 1
        board[1, 4] = 2
        
        winner, loser = self.game.get_winner()
        self.assertEqual(winner, None)
    
    def test_win_dia_with_other(self, p=1):
        board = self.game.board
        # Construct winning situation.
        board[0, 0] = 3 - p
        for i in xrange(1, 6):
            board[i, i] = p
        
        # See whether the winner has been found.
        winner, loser = self.game.get_winner()
        self.assertNotEqual(winner, None)
        self.assertEqual(winner.uid, p)

    def test_set(self):
        i = 1
        board = self.game.board
        for r in xrange(6):
            for c in xrange(6):
                board[r, c] = i
                self.assertEquals(board[r, c], i)
                if i == 2:
                    i = 0
                else:
                    i += 1


if core.EXTENSION_MODULE:
    from pypentago import _board
    class TestFallback(TestGame):
        def setUp(self):
            core.Board = board.Board
            TestGame.setUp(self)
        
        def tearDown(self):
            core.Board = _board.Board
else:
    class TestFallback(TestGame):
        pass
    del TestGame

if __name__ == "__main__":
    unittest.main()
