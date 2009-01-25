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
from pypentago import core
from pypentago import board
from pypentago.exceptions import (SquareNotEmpty, NotYourTurn, GameFull,
                                  InvalidTurn)
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
    
    def test_api(self):
        self.assert_(hasattr(self.game.board, 'set_pos'))
        self.assert_(hasattr(self.game.board, 'get_pos'))
        self.assert_(hasattr(self.game.board, 'rotate_cw'))
        self.assert_(hasattr(self.game.board, 'rotate_ccw'))
        self.assert_(hasattr(self.game.board, '__getitem__'))
        self.assert_(hasattr(self.game.board, '__setitem__'))
    
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
    
    def test_win_dia(self, p=1, x=0):
        board = self.game.board
        # Construct winning situation.
        board[0 + x, 0 + x] = p
        board[1 + x, 1 + x] = p
        board[2 + x, 2 + x] = p
        board[3 + x, 3 + x] = p
        board[4 + x, 4 + x] = p

        # See whether the winner has been found.
        winner, loser = self.game.get_winner()
        self.assertNotEqual(winner, None)
        self.assertEqual(winner.uid, p)
    
    def test_win_dia_p2(self):
        self.test_win_dia(2)
    
    def test_win_dia_four(self, p=1):
        self.test_win_dia(p, 1)
    
    def test_win_dia_four_p2(self):
        self.test_win_dia_four(2)

    def test_win_dia_sec(self, p=1):
        board = self.game.board
        # Construct winning situation.
        board[0, 1] = p
        board[1, 2] = p
        board[2, 3] = p
        board[3, 4] = p
        board[4, 5] = p

        # See whether the winner has been found.
        winner, loser = self.game.get_winner()
        self.assertNotEqual(winner, None)
        self.assertEqual(winner.uid, p)
    
    def test_win_dia_sec_p2(self):
        self.test_win_dia_sec(2)

    def test_win_dia_tert(self, p=1):
        board = self.game.board
        # Construct winning situation.
        board[1, 0] = p
        board[2, 1] = p
        board[3, 2] = p
        board[4, 3] = p
        board[5, 4] = p

        # See whether the winner has been found.
        winner, loser = self.game.get_winner()
        self.assertNotEqual(winner, None)
        self.assertEqual(winner.uid, p)
    
    def test_win_dia_tert_p2(self):
        self.test_win_dia_tert(2)
    
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
        p_2.opponent_quit = fail
        self.assertRaises(Called, p_1.quit_game)

if core.EXTENSION_MODULE:
    from pypentago import _board
    class TestFallback(TestGame):
        def setUp(self):
            core.Board = board.Board
            TestGame.setUp(self)
        
        def tearDown(self):
            core.Board = _board.Board


if __name__ == "__main__":
    unittest.main()
