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

from __future__ import with_statement

import sys
import logging

import actions

from hashlib import sha1 as sha
from string import ascii_letters
from random import randint, choice
    
from pypentago import PROTOCOL_VERSION
from pypentago import core
from pypentago import crypto
from pypentago.server import core as s_core
from pypentago.get_conf import get_conf_obj
from pypentago.server import db
from pypentago.server.mailing import Email
from pypentago.server.db.dbobjs import Player
from pypentago.exceptions import NoSuchRoom, NotInDB

from easy_twisted.server import Connection
from easy_twisted.connection import expose, require_auth


conf = get_conf_obj('server')

email_text = ("Dear %(real_name)s,\n"
              "Thank you for registering with pypentago.\n"
              "Your verification code is %(code)s. \n"
              "Please use the "
              "\"Activate Account\" dialog for activating your account.\n"
              "\n"
              "Please note that it is forbidden to register multiple "
              "accounts for one person.")


class Conn(Connection):
    def init(self):
        self.log = logging.getLogger("pypentago.connection")
        self.log.info("Got connection from %s" % self.transport.getPeer().host)
        
        self.server = self.factory
        self.name = "Player"
        self.remote_table = {}
        self.expect_response = None
        
    @expose("GAME")
    @require_auth
    def remote_dispatcher(self, evt):
        game_id = evt['data'][0]
        rest = evt['data'][1:]
        
        if game_id not in self.remote_table:
            # Notify other side that the game is not known
            pass
        else:
            remote = self.remote_table[game_id]
            cmd = rest[0]
            arg = rest[1:]
            remote.lookup(cmd)(*arg)
    
    @expose("OPEN")
    @require_auth
    def open_game(self, evt):
        name = evt['data']
        game = s_core.ServerGame(name)
        uid = self.server.next_game_id()
        p = core.RemotePlayer(self)
        game.uid = uid
        self.remote_table[uid] = p
        self.server.games[uid] = game
        game.add_player(p)
        return "OPENGAME", uid
    
    @expose("JOIN")
    @require_auth
    def join_game(self, evt):
        uid = evt['data']
        p = core.RemotePlayer(self)
        g = self.server.games[uid]
        g.add_player(p)
        self.remote_table[uid] = p
        b = g.random_beginner()
        self.send("INITGAME", uid)
        g.other_player(self).conn.send("INITGAME", uid)
        b.conn.send("GAME", [uid, "LOCALTURN"])
    
    @expose("REGISTER")
    def register(self, evt):
        d = evt['data']
        p = Player(d['login'], crypto.hash_pwd(d['passwd']),
                   d['real_name'], d['email'])
        if db.login_available(d['login']):
            with db.transaction() as session:
                session.save(p)
            self.send('REGISTERED')
        else:
            self.send('REGFAILED')
    
    @expose("LOGIN")
    def login(self, evt):
        try:
            p = db.player_by_login(evt['data']['login'])
        except NotInDB:
            return "NOLOGIN"
        
        if crypto.check_pwd(p.passwd_hash, evt['data']['passwd']):
            self.auth = True
            return "AUTH"
        else:
            return "AUTHF"
