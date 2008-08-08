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


from pypentago.server.db.player import Player
from pypentago.server.db.playermanager import DuplicateLoginError
from pypentago.server.db.playermanager import NotInDbError
from pypentago.server.db.managers import player_manager
import unittest

class PlayerManagerTest(unittest.TestCase):

    def setUp(self):
        self.mManager = player_manager
        result = self.mManager.get_players()
        self.login = []
        if result.count() < 1:
            player = Player("asdasd", 40*"a", "Test Player", "player@test.at", 
                            "I'm a noob")
            self.login.append("asdasd")
            self.mManager.save_player(player)

    def tearDown(self):
        for login in self.login:
            self.mManager.delete_player_by_login(login)
    def testGetPlayers(self):
        result = self.mManager.get_players()
        self.assertNotEqual(None, result)
        size = result.count()
        self.assertNotEqual(0,size)
        for player in result:
            print
            print player

    def testGetPlayerById(self):
        lplayers = self.mManager.get_players()
        self.assertNotEqual(0, lplayers.count())
        lplayer = lplayers.first()
        id = lplayer.player_id
        player1 = self.mManager.get_player_by_id(id)
        self.assertEqual(id, player1.player_id)
            
    def testGetPlayerByLogin(self):
        lplayers = self.mManager.get_players()
        self.assertNotEqual(0,lplayers.count())
        lplayer = lplayers.first()
        login = lplayer.player_name
        player = self.mManager.get_player_by_login(login)
        
        self.assertEqual(login, player.player_name)
        #for player in players:
        #    print "\n"
        #   print player
        #    self.assertEqual(login, player.player_name)
        

    def testSaveDeletePlayer(self):
        from pypentago import get_rand_str
        rand_login = get_rand_str()
        while self.mManager.get_player_by_login(rand_login):
            rand_login = get_rand_str()
        lPlayer = Player(rand_login, 40*"f", 
                         'Google Yahoo', 'mail33@google.com', 'something')
        self.mManager.save_player(lPlayer)
        playerInDb = self.mManager.get_player_by_login(rand_login)


        self.assertEqual(lPlayer, playerInDb)
        
        self.mManager.delete_player_by_login(rand_login)
        playerInDb = self.mManager.get_player_by_login(rand_login)
    

        self.assertEqual(None,playerInDb)
    
    def testSaveDuplicateLogin(self):
        lplayers = self.mManager.get_players()
        self.assertNotEqual(0,lplayers.count())
        lplayer = lplayers.first();
        new_player = Player(lplayer.player_name, 
                            '90288476ed183000f2b46904d5667633a9a11585', 
                            'Google Yahoo', 'mail33@google.com',
                            'something')
        
        self.assertRaises(DuplicateLoginError, self.mManager.save_player, 
                          new_player)
    
    def testUpdatePlayer(self):
        lplayers = self.mManager.get_players()
        self.assertNotEqual(0, lplayers.count())
        lplayer = lplayers.first()
        lplayer.real_name = "Updated Name"
        self.mManager.update_player(lplayer)
        
        player_in_db = self.mManager.get_player_by_id(lplayer.player_id)
        
        self.assertEqual('Updated Name', player_in_db.real_name)    
            
            
if __name__ == '__main__':
    unittest.main()
