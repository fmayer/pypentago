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


# Fix the PYTHONPATH so we needn't have src in it.
import sys
from os.path import dirname, abspath, join
sys.path.append(abspath(join(dirname(__file__), "..")))
# End of prefix for executable files.

import unittest
from pypentago.core import Game, Player
from pypentago.exceptions import SquareNotEmpty, NotYourTurn, GameFull

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.players = [Player() for _ in xrange(2)]
        for p in self.players:
            self.game.add_player(p)
    
    def test_win_dia(self):
        board = self.game.board
        # Construct winning situation.
        board[0][0][0] = 2
        board[0][1][1] = 2
        board[0][2][2] = 2
        board[3][0][0] = 2
        board[3][1][1] = 2

        # See whether the winner has been found.
        winner, loser = self.game.get_winner()
        self.assertNotEqual(winner, None)
        self.assertEqual(winner.uid, 2)

    def test_win_dia_sec(self):
        board = self.game.board
        # Construct winning situation.
        board[0][0][1] = 2
        board[0][1][2] = 2
        board[1][2][0] = 2
        board[3][0][1] = 2
        board[3][1][2] = 2

        # See whether the winner has been found.
        winner, loser = self.game.get_winner()
        self.assertNotEqual(winner, None)
        self.assertEqual(winner.uid, 2)

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
        def fail(*args, **kw):
            raise NotImplementedError
        p_1, p_2 = self.players
        p_2.display_turn = fail
        # See if p_2.display_turn gets called
        self.assertRaises(NotImplementedError, p_1.do_turn, (1, 0, 0, "R", 1))
    
    def test_beginner(self):
        beginner = self.game.random_beginner()
        other = self.game.other_player(beginner)
        self.assertRaises(NotYourTurn, other.do_turn, (1, 0, 0, "R", 1))
        self.assertEqual(beginner.do_turn((1, 0, 0, "R", 1)), None)
    
    def test_other(self):
        one, other = self.players
        self.assert_(self.game.other_player(one) is other)
        self.assert_(self.game.other_player(other) is one)


if __name__ == "__main__":
    unittest.main()
