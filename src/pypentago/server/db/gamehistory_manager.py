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

from sessionmanager import SessionManager
from gamehistory import GameHistory

class GameHistoryManager:
    def __init__(self, session_manager):
        self.mSessionManager = session_manager
        
    def save_gamehistory(self, aGameHistory):
        self.mSessionManager.save_single(aGameHistory)
    
    def get_all_gamehistory(self):
        return self.mSessionManager.get_session().query(GameHistory)
    
    def getGameHistoryById(self, aId):
        return self.mSessionManager.get_session().query(GameHistory).get(aId)
    
    def deleteGameHistoryById(self, aId):
        del_gm_history = self.getGameHistoryById(aId)
        if None == del_gm_history:
            return
        self.mSessionManager.delete_single(del_gm_history)
        
    def get_last_played_game(self):
        qstr = "select * from gamehistory order by time_stamp desc"
        res = self.mSessionManager.get_session().query(GameHistory).from_statement(qstr).all()
        return res[0]
    
    def games_played_by_player(self, player_id):
        qstr = "select * from gamehistory where winner_id = :p_id or loser_id = :p_id"
        return self.mSessionManager.get_session().query(GameHistory).from_statement(qstr).params(p_id=player_id).all()
    
    def games_won_by_player(self, player_id):
        qstr = "select * from gamehistory where winner_id = :p_id"
        return self.mSessionManager.get_session().query(GameHistory).from_statement(qstr).params(p_id=player_id).all()
     
    