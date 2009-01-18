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

if __name__ == '__main__':
    from os.path import dirname, join
    sys.path.append(join(dirname(__file__), '..', '..'))

import actions

from pypentago import PROTOCOL_VERSION, could_int, int_all
from pypentago.core import Game
from pypentago.client import context
from pypentago.core import RemotePlayer
from pypentago.client.interface import new_game

from easy_twisted.connection import expose, Connection

log = logging.getLogger("pypentago.connection")

ID_WIN = 1
ID_DRAW = 0.5
ID_LOST = 0
ID_CONN_LOST = -1

ID_DUP = 0.5
ID_REG = True
ID_NOT_REG = False


class ClientConnection(Connection):
    def init(self):
        # This maps the game-id to the remote player.
        self.factory.callback(self)
        self.remote_table = {}
        log.info("Connection established")
        context.emmit_action('conn_established', self)
    
    def register(self, login, passwd, real_name, email):
        self.send("REGISTER", {'login': login, 'passwd': passwd,
                               'real_name': real_name, 'email': email})
    
    def authenticate(self, login, passwd):
        self.send("LOGIN", {'login': login, 'passwd': passwd})
    
    def open_game(self, name):
        self.send("OPEN", name)
    
    def join_game(self, uid):
        self.send("JOIN", uid)
    
    @expose("INITGAME")
    def init_game(self, evt):
        game = Game()
        new_game(game)
        r = RemotePlayer(self)
        self.remote_table[evt['data'][0]] = r
        game.add_player(r)
    
    @expose("GAME")
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
    
    @expose("AUTH")
    def auths(self):
        pass
    
    @expose("AUTHF")
    def authf(self):
        pass
    
    @expose("REGISTERED")
    def registered(self):
        pass
    
    @expose("REGFAILED")
    def reg_failed(self):
        pass
    
    @classmethod
    def start_new(cls, host, port, callback=None):
        from twisted.internet import reactor, protocol
        f = protocol.ClientFactory()
        f.protocol = cls
        f.callback = callback
        reactor.connectTCP(host, port, f)


if __name__ == '__main__':
    test = ClientConnection()
