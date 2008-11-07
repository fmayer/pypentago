# Prefix any executable file with this to set the correct PYTHONPATH:
import sys
from os.path import dirname, abspath, join
script_path = dirname(__file__)
sys.path.append(abspath(join(script_path, ".."))) # Adjust to number
                                                   # of subdirs the current
                                                   # file is in.
# End of prefix for executable files.

import unittest
from pypentago.core import Game, Player
from pypentago.exceptions import SquareNotEmpty

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game((Player(), Player()))
    
    def test_win_dia(self):
        board = self.game.board
        # Construct winning situation.
        board[0][0][0] = 2
        board[0][1][1] = 2
        board[0][2][2] = 2
        board[3][0][0] = 2
        board[3][1][1] = 2

        # See whether the winner has been found.
        winner = self.game.get_winner()
        self.assertNotEqual(winner, False)
        self.assertEqual(winner[0].uid, 2)

    def test_win_dia_sec(self):
        board = self.game.board
        # Construct winning situation.
        board[0][0][1] = 2
        board[0][1][2] = 2
        board[1][2][0] = 2
        board[3][0][1] = 2
        board[3][1][2] = 2

        # See whether the winner has been found.
        winner = self.game.get_winner()
        self.assertNotEqual(winner, False)
        self.assertEqual(winner[0].uid, 2)

    def test_square_not_empty(self):
        self.game.apply_turn(self.game.players[0], (0, 0, 0, "R", 1))
        self.assertRaises(SquareNotEmpty, self.game.apply_turn, 
                          self.game.players[1], (0, 0, 0, "R", 1))


if __name__ == "__main__":
    unittest.main()
