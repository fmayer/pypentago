#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pyPentago - a board game
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

# Prefix any executable file with this to set the correct PYTHONPATH:
import sys
from os.path import dirname, abspath, join
script_path = dirname(__file__)
sys.path.append(abspath(join(script_path, ".."))) # Adjust to number
                                                              # of subdirs the current
                                                              # file is in.
# End of prefix for executable files.

from pypentago.server.db.gamehistory import GameHistory
from pypentago.server.db.gamehistory_manager import GameHistoryManager
from pypentago.server.db.managers import game_history_manager
import unittest

class GameHistoryManagerTest(unittest.TestCase):
    
    def setUp(self):
        self.Manager = game_history_manager
        game_history = GameHistory(1, 1, 1400, 1400, "asdasd", "asdafds")
        
        self.Manager.save_gamehistory(game_history)
    
    def test_get_all_gamehistory(self):
        list = self.Manager.get_all_gamehistory()
        self.assertNotEqual(None, list)
        self.assertNotEqual(0, list.count())
        for gh in list:
            print "\n"
            print gh
    
    def test_getGameHistoryById(self):
        game_history = GameHistory(1, 1, 1400, 1400, "asdasd", "asdafds")
        
        self.Manager.save_gamehistory(game_history)
        
        list = self.Manager.get_all_gamehistory()
        self.assertNotEqual(None,list)
        lGameHistory = list.first()
        lId = lGameHistory.game_id
        game_history_in_db = self.Manager.getGameHistoryById(lId)
        self.assertEqual(lId,game_history_in_db.game_id)
        print game_history_in_db
    
    def testSaveAndDeleteGameHistory(self):
        game_history = GameHistory(1, 1, 1400, 1400, "asdasd", "asdafds")
        
        self.Manager.save_gamehistory(game_history)
        game_history_in_db = self.Manager.get_last_played_game()
        self.assertEqual(game_history,game_history_in_db)
        
        id = game_history_in_db.game_id
        ts = game_history_in_db.time_stamp
        
        self.Manager.deleteGameHistoryById(id)
        
        game_history_in_db = self.Manager.getGameHistoryById(id)
        self.assertEqual(None, game_history_in_db)
    
    def test_games_played_by_player(self):
        id = 1
        result = self.Manager.games_played_by_player(id)
        #self.assertTrue(True)
        for gh in result:
            check = (gh.winner_id == id or gh.loser_id == id)
            self.assertTrue(check)
            print "\n"
            print gh
        
    def test_games_won_by_player(self):
        id = 2
        result = self.Manager.games_won_by_player(id)        
        for gh in result:
            self.assertEqual(id,gh.winner_id)
            print "\n"
            print gh
    
if __name__ == '__main__':
    unittest.main()
        
