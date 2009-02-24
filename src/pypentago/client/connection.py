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

from hashlib import sha1 as sha
from functools import partial

import sys
import logging

import actions

from twisted.internet import protocol

from pypentago import PROTOCOL_VERSION
from pypentago.core import Game
from pypentago.client import context
from pypentago.core import RemotePlayer

from easy_twisted.connection import expose, Connection

log = logging.getLogger("pypentago.connection")
exception_log = logging.getLogger("pypentago.exception")

ID_WIN = 1
ID_DRAW = 0.5
ID_LOST = 0
ID_CONN_LOST = -1

ID_DUP = 0.5
ID_REG = True
ID_NOT_REG = False


class ClientConnection(Connection):
    def init(self):
        self.factory.callback(self)
        #: This maps the game-id to the remote player.
        self.remote_table = {}
        log.info("Connection established")
        context.emmit_action('conn_established', self)
        self.name = None
        self.login_as = None
        self.server_window = self.factory.parent
    
    def register(self, login, passwd, real_name, email):
        self.send("REGISTER", {'login': login, 'passwd': passwd,
                               'real_name': real_name, 'email': email})
    
    def authenticate(self, login, passwd):
        self.login_as = login
        self.send("LOGIN", {'login': login, 'passwd': passwd})
    
    def new_game(self, name):
        self.send("OPEN", name)
    
    def join_game(self, uid):
        self.send("JOIN", uid)
    
    @expose("OPENGAME")
    def open_game(self, evt):
        # TODO: Debug code follows.
        gid = evt['data']
        print "Opened game with id %d" % gid
    
    @expose("INITGAME")
    def init_game(self, evt):
        di = evt['data']
        game = Game()
        game.uid = di['game_id']
        
        local_player = self.server_window.player_cls()
        local_player.name = self.name
        local_player.uid = di['player_id']
        r = RemotePlayer(self, di['opponent_name'])
        r.uid = 3 - di['player_id']
        self.remote_table[di['game_id']] = r
        game.add_player_with_uid(r)
        game.add_player_with_uid(local_player)
        if di['beginner']:
            game.last_set = r
        else:            
            game.last_set = local_player
        
        self.server_window.show_game(local_player)
    
    @expose("GAME")
    def remote_dispatcher(self, evt):
        game_id, cmd, args = evt['data']
        
        if game_id not in self.remote_table:
            self.send("INVGAME")
        else:
            remote = self.remote_table[game_id]
            arg = remote.game.unrpcialize(args)
            remote.lookup(cmd)(*arg)
    
    @expose("AUTH")
    def auths(self):
        self.name = self.login_as
    
    @expose("AUTHF")
    def authf(self):
        pass
    
    @expose("REGISTERED")
    def registered(self):
        pass
    
    @expose("REGFAILED")
    def reg_failed(self):
        pass
    
    @expose("GAMES")
    def games(self, evt):
        self.server_window.show_games(evt['data'])
    
    @classmethod
    def start_new(cls, host, port, parent, callback=None):
        from twisted.internet import reactor
        host = str(host)
        port = int(port)
        f = protocol.ClientFactory()
        f.protocol = cls
        f.callback = callback
        f.parent = parent
        f.clients = []
        reactor.connectTCP(host, port, f)
    
    def internal_error(self, request):
        exception_log.critical(
            "Internal server error handling request %r" % request,
            exc_info=True
        )
    
    def bad_input(self, request):
        exception_log.critical(
            "Bad input at request %r" % request,
            exc_info=True
        )
    
    def malformed_request(self, request):
        exception_log.critical(
            "Malformed request %r" % request,
            exc_info=True
        )
    
    def no_handler(self, request):
        exception_log.critical(
            "No handler found for request %r" % request,
            exc_info=True
        )


if __name__ == '__main__':
    test = ClientConnection()
