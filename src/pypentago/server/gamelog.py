#! /usr/bin/env python
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

from pypentago.server.db import player, player_manager, gamehistory
from pypentago.server.db import game_history_manager
from pypentago.server.glicko2 import RatingCalculator

class GameLog(object):

    def __init__(self, p1, p2):
        """p1 is always the winner here."""
        #1 get both players player database objects using the playermanager
        p_manager = player_manager
        self.player1 = p_manager[p1.database_id]
        self.player2 = p_manager[p2.database_id]

    def write_game(self):
        """public function to log game to database.   
           Remember, player1 was the winner here."""
        #1 get both players player database objects using the playermanager
        #player objects already gotten by init
        #2 get a gamehistory database object
        self.gamehist = gamehistory.GameHistory(self.player1.id, self.player2.id,
                                                self.player1.rating, self.player1.rd, self.player1.volatility,
                                                self.player2.rating, self.player2.rd, self.player2.volatility,
                                                "not yet implemented", "not yet implemented")
        #3 insert the gamehistory object into the database using the gamehistory_manager
        gh = game_history_manager
        gh.save_gamehistory(self.gamehist)
