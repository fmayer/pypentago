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

from __future__ import with_statement

import sys
import time
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

from easy_twisted.connection import expose, require_auth, Connection


conf = get_conf_obj('server')
exception_log = logging.getLogger("pypentago.exception")

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
        self.db_player = None
        self.name = "Player"
        self.remote_table = {}
        self.expect_response = None
    
    def destruct(self, reason):
        self.logout(answer=False)
        
    @expose("GAME")
    @require_auth
    def remote_dispatcher(self, evt):
        game_id = evt['data'][0]
        rest = evt['data'][1:]
        
        if game_id not in self.remote_table:
            self.send("INVGAME")
        else:
            remote = self.remote_table[game_id]
            cmd = rest[0]
            arg = rest[1:]
            remote.lookup(cmd)(*arg)
    
    @expose("LOGOUT")
    @require_auth
    def logout(self, evt=None, answer=True):
        for p in self.remote_table.itervalues():
            p.quit_game()
        self.auth = False
        self.db_player = None
        if answer:
            self.send("LOGGEDOUT")
    
    @expose("OPEN")
    @require_auth
    def open_game(self, evt):
        name = evt['data']
        game = s_core.ServerGame(name)
        uid = self.server.next_game_id()
        p = core.RemotePlayer(self, self.db_player.player_name)
        game.uid = uid
        self.remote_table[uid] = p
        self.server.games[uid] = game
        game.add_player(p)
        return "OPENGAME", uid
    
    @expose("JOIN")
    @require_auth
    def join_game(self, evt):
        gid = evt['data']
        player = core.RemotePlayer(self, self.db_player.player_name)
        game = self.server.games[gid]
        game.add_player(player)
        self.remote_table[gid] = player
        beginner = game.random_beginner()
        for player in game.players:
            player.conn.send(
                "INITGAME", 
                {'game_id': gid,
                 'player_id': player.uid,
                 'beginner': player is beginner,
                 'opponent_name': game.other_player(player).name
                 }
            )
    
    @expose("GAMELIST")
    @require_auth
    def game_list(self, evt=None):
        self.send(
            "GAMES", 
            [game.serialize() for game in self.server.games.itervalues()]
        )
    
    @expose("REGISTER")
    def register(self, evt):
        d = evt['data']
        p = Player(d['login'], crypto.hash_pwd(d['passwd']),
                   d['real_name'], d['email'])
        if self.factory.database.login_available(d['login']):
            with self.factory.database.transaction as session:
                session.save(p)
            self.send('REGISTERED')
        else:
            self.send('REGFAILED')
    
    @expose("LOGIN")
    def login(self, evt):
        try:
            p = self.factory.database.player_by_login(evt['data']['login'])
        except NotInDB:
            return "NOLOGIN"
        
        if crypto.check_pwd(p.passwd_hash, evt['data']['passwd']):
            self.auth = True
            self.db_player = p
            self.send("AUTH")
            self.game_list()
        else:
            return "AUTHF"
    
    def internal_error(self, request):
        exception_log.critical(
            "Internal server error handling request %r" % request,
            exc_info=True
        )
        self.send("INTERNALERROR", (time.time(), request))
    
    def bad_input(self, request):
        exception_log.critical(
            "Bad input at request %r" % request,
            exc_info=True
        )
        self.send("BADINPUT", (time.time(), request))
    
    def malformed_request(self, request):
        exception_log.critical(
            "Malformed request %r" % request,
            exc_info=True
        )
        self.send("MALFORMED", (time.time(), request))
    
    def no_handler(self, request):
        exception_log.critical(
            "No handler found for request %r" % request,
            exc_info=True
        )
        self.send("NOHANDLER", (time.time(), request))
