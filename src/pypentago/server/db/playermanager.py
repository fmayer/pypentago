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
from player import Player

class DuplicateLoginError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value) 

class NotInDbError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class PlayerManager:

    def __init__(self, session_manager):
        self.mSessionManager = session_manager
    def __getitem__(self,  key):
        if type(key) == str:
            return self.get_player_by_login(item)
        elif type(key) == int:
            return self.get_player_by_id(item)
    def __delitem__(self,  key):
        if type(key) == str:
            self.delete_player_by_login(key)
        elif type(key) == int:
            self.delete_player_by_id(key)
    def __contains__(self, key):
        return self.login_available(key)
    def save_player(self, aPlayer):
        login = aPlayer.player_name
        if self.login_available(login):
            self.mSessionManager.save_single(aPlayer)
        else:
            e_str =  'Error: duplicate login: '+login
            raise DuplicateLoginError(e_str)
        
    def update_player(self, player):
        id = player.player_id
        player_in_db = self.get_player_by_id(id)
        if None == player_in_db:
            e_str = ("Player %s not found in db cannot update " 
                     % player.player_name)
            raise NotInDbError(e_str)
        self.mSessionManager.update_single(player)

    def get_players(self):
        return self.mSessionManager.get_session().query(Player)

    def get_player_by_id(self, aId):
        return self.mSessionManager.get_session().query(Player).get(aId)

    def search_by_realname(self, keyword):
        qstr = "%"+keyword+"%"
        return self.mSessionManager.get_session().query(Player).filter(
            Player.real_name.like(qstr))

    def delete_player_by_login(self, login):
        del_list = self.mSessionManager.get_session().query(Player).filter_by(
            player_name=login)
        for player in del_list:
            self.mSessionManager.delete_single(player)

    def delete_player_by_id(self, aId):
        del_player = self.get_player_by_id(aId)
        if None == del_player:
            return
        self.mSessionManager.delete_single(del_player)

    def login_available(self, login):
        pl_list = self.mSessionManager.get_session().query(Player).filter_by(
            player_name=login)
        if 0 == pl_list.count():
            return True
        else:
            return False

    def email_available(self, email):
        pl_list = self.get_player_by_email(email)
        if pl_list.count() == 0:
            return True
        else:
            return False

    def get_player_by_email(self, email):
        return self.mSessionManager.get_session().query(Player).filter_by(
            player_email=email)

    def get_player_by_login(self, aLogin):
        players =  self.mSessionManager.get_session().query(Player).filter_by(
            player_name=aLogin)
        if players.count() <= 0:
            return None
        return players[0]
