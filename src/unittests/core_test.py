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
from pypentago.exceptions import SquareNotEmpty, NotYourTurn, GameFull

class TestGame(unittest.TestCase):
    def setUp(self):
        self.game = Game()
        self.players = [self.game.new_player(),
                        self.game.new_player()]
    
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
        self.assertRaises(GameFull, self.game.new_player)
    
    def test_players(self):
        def fail(*args, **kw):
            raise NotImplementedError
        p_1, p_2 = self.players
        p_2.display_turn = fail
        # See if p_2.display_turn gets called
        self.assertRaises(NotImplementedError, p_1.do_turn, (1, 0, 0, "R", 1))
        


if __name__ == "__main__":
    unittest.main()
