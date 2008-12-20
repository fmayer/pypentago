#! /usr/bin/env python
# -*- coding: us-ascii -*-

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
from pypentago.client.core import RemotePlayer
from pypentago.client.interface import new_game

from easy_twisted.connection import expose
from easy_twisted.client import Connection

log = logging.getLogger("pypentago.connection")

ID_WIN = 1
ID_DRAW = 0.5
ID_LOST = 0
ID_CONN_LOST = -1

ID_DUP = 0.5
ID_REG = True
ID_NOT_REG = False


class InvalidIPException(Exception):
    pass


class Player:
    def __init__(self, player_name, real_name, current_rating, player_profile):
        self.login = player_name
        self.real_name = real_name
        self.current_rating = current_rating
        self.profile = player_profile


class GameInfo:
    def __init__(self, id, name, player, score, full, ranked, conn):
        self.id = id
        self.name = name 
        self.score = score
        self.player = player
        self.full = full
        self.conn = conn
        self.ranked = ranked
    
    def join(self):
        self.conn.join_game(self.id)


class Conn(Connection):
    def init(self):
        # This maps the game-id to the remote player.
        self.remote_table = {}
        log.info("Connection established")
        context.emmit_action('conn_established', self)
    
    def init_game(self, evt):
        game = Game()
        new_game(game)
        r = RemotePlayer(self)
        self.remote_table[evt['id']] = r
        game.add_player(r)

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
        
    @expose('PWDCHANGED')
    def passwd_changed(self, evt):
        pass
    
    @expose('WRONGPWD')
    def wrong_passwd(self, evt):
        pass
    
    def change_password(self, old_pwd, new_pwd):
        self.send("CHPWD", (sha(old_pwd).hexdigest(), sha(new_pwd).hexdigest()))
    
    def get_player(self, login):
        self.send("GETPLAYER", login)
        
    @expose('PLAYER')
    def recv_player(self, evt):
        (player_name, real_name, current_rating, player_profile) = evt.arg_list
        player = Player(player_name, real_name, current_rating, player_profile)
        context.emmit_action('display_player', player)
    
    @expose('DUPNAME')
    def dup_name(self, evt):
        context.emmit_action('registered', ID_DUP)
    
    @expose('NOTLOGGEDIN')
    def not_logged_in(self, evt):
        context.emmit_action('not_logged_in')
    
    def request_protocol_version(self, evt):
        self.send("PROTVERSION", PROTOCOL_VERSION)
    
    @expose('PROTVERSION')
    def protocol_version(self, evt):
        server_prot = int(evt.arg_list[0])
        if server_prot != PROTOCOL_VERSION:
            log.error("Server protocol does not match client protocol!")
    
    @expose('SYNCGAMES')
    def sync_gamelist(self, evt):
        self.get_games()
    # LOGIN FUNCTIONS
    # -------------------------
    def login(self, name, passwd):
        log.debug("Initiated login")
        self.send("INITLOGIN", name)
        self.passwd = passwd
    
    @expose('CHALLENGE')
    def on_challenge(self, evt):
        log.debug("Received Challenge")
        temp_login = evt.arg
        self.respond(temp_login)

    def respond(self, temp_login):
        log.debug("Generating response")
        passwd_hash = sha(self.passwd).hexdigest()
        send = sha(temp_login+passwd_hash).hexdigest()
        log.debug("Sending response")
        self.send("RESPONSE", send)
    
    @expose('LOGINS')
    def login_success(self, args):
        context.emmit_action('login', True)
    
    @expose('LOGINF')
    def login_failure(self, args):
        context.emmit_action('login', False)
    # LOGIN FUNCTIONS END
    # -------------------------
    
    # USER WIZARD FUNCTIONS
    # -------------------------
    def name_availability(self, name):
        self.send("NAMEAVAIL", name)
        log.debug("Sent NAMEAVAIL")
    
    def email_availability(self, email):
        self.send("EMAILAVAIL", email)
        
        log.debug("Sent EMAILAVAIL")
        
    @expose('EMAILUNAVAIL')
    def on_email_unavailable(self, evt):
        context.emmit_action('email_available', False)
    
    @expose('EMAILAVAIL')
    def on_email_available(self, evt):
        context.emmit_action('email_available', True)
    
    @expose('NAMEUNAVAIL')
    def on_name_unavailable(self, evt):
        context.emmit_action('name_available', False)

    @expose('NAMEAVAIL')
    def on_name_available(self, evt):
        context.emmit_action('name_available', True)
    # USER WIZARD FUNCTIONS END
    # -------------------------

    def close_game(self):
        self.send("CLOSEGAME")
    
    @expose('GAMEFULL')
    def on_game_full(self, evt):
        pass
    
    @expose('NOSUCHGAME')
    def no_such_game(self, evt):
        self.get_games() # To synchronize the gamelist again
    
    def onAny(self, evt):
        log.warn("Received unknown event\n"
                      "Keyword: %s\n" 
                      "Arguments: %s" % (evt.keyword,
                                         evt.arg_list
                                         )
                      )
    
    def destruct(self, reason):
        log.warn("Connection to server lost")
    
    @expose('CONNLOST')
    def on_conn_lost(self, evt):
        context.emmit_action('conn_lost', ID_CONN_LOST)
    
    @expose('WON')
    def on_won(self, evt):
        context.emmit_action('game_over', ID_WIN)
    
    @expose('LOST')
    def on_lost(self, evt):
        context.emmit_action('game_over', ID_LOST)
    
    @expose('JOINEDGAME')
    def joined(self, evt):
        pass

    def host_game(self, name, ranked=False):
        log.debug("HOSTGAME %s %s" % (name, ranked))
        self.send("HOSTGAME", (name, int(ranked)))

    def get_games(self):
        self.send("GETGAMES")
    
    @expose('GAMES')
    def on_games(self, evt):
        games = evt.arg_list
        r_games = []
        for game in games:
            if game:
                id, name, player, score, full, ranked = game
                if name.strip() != "":
                    r_games.append(GameInfo(str(id), name, player, str(score), 
                                            full, ranked, self))
        context.emmit_action('gamelist', r_games)

    def join_game(self, id):
        self.send("JOINGAME", id)
        
    @expose('INGAME')
    def on_in_game(self, evt):
        log.warn("Already in a room")
        context.emmit_action('in_game')
    
    @expose('START')
    def on_start(self, evt):
        log.info("Game started")
        self.active = False
        context.emmit_action('start', False)
    
    @expose('NOTYOURTURN')
    def on_not_turn(self, evt):
        log.warn("Not your turn!")
        if self.active:
            log.error("Client self.active wrong!")
            self.active = False
        else:
            log.error("Server does not accept client turn although "
                      "self.active = True at the client")
    
    def do_turn(self, field, row, position, rot_dir, rot_field):
        if self.active:
            self.send("DOTURN", (str(field), str(row), str(position), rot_dir, 
                                 rot_field))
            self.active = False
        
    @expose('YOURTURN')
    def on_turn(self, evt):
        log.debug("Received TURN %s " % str(evt.arg_list))
        context.emmit_action('turn_recv', evt.arg_list)
        self.active = True
    
    @expose('BEGIN')
    def on_begin(self, evt):
        log.debug("Received BEGIN")
        self.active = True
        context.emmit_action('start', True)
        
    @expose('REGISTERED')
    def registered(self, evt):
        context.emmit_action('registered', ID_REG)


def run_client(host, port):
    from twisted.internet import reactor, protocol
    f = protocol.ClientFactory()
    f.protocol = Conn
    f.clients = []
    reactor.connectTCP(host, port, f)


if __name__ == '__main__':
    test = Conn()
    print test.binds.keys()
