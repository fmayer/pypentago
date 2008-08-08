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

from sha import sha
from functools import partial
import sys
import logging

from wx import CallAfter, MessageDialog, OK, ICON_INFORMATION

if __name__ == '__main__':
    from os.path import dirname, join
    sys.path.append(join(dirname(__file__), '..', '..'))

from pypentago import PROTOCOL_VERSION, could_int, int_all
from pypentago import actions

from easy_twisted.connection import expose
from easy_twisted import evt
from easy_twisted.client import Connection

log = logging.getLogger("pypentago.connection")

ID_WIN = 1
ID_DRAW = 0.5
ID_LOST = 0

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
        self.conn.joinGame(self.id)


class Conn(Connection):
    def init(self):
        log.info("Connection established")
        actions.emmit_action('conn_established', self)
        self.active = False
        self.getGames()
        
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
        actions.emmit_action('display_player', player)
    
    @expose('DUPNAME')
    def dup_name(self, evt):
        actions.emmit_action('registered', ID_DUP)
    
    @expose('NOTLOGGEDIN')
    def not_logged_in(self, evt):
        actions.emmit_action('not_logged_in')
    
    def request_protocol_version(self, evt):
        self.send("PROTVERSION", PROTOCOL_VERSION)
    
    @expose('PROTVERSION')
    def protocol_version(self, evt):
        server_prot = int(evt.arg_list[0])
        if not server_prot == PROTOCOL_VERSION:
            log.error("Server protocol does not match client protocol!")
    
    @expose('SYNCGAMES')
    def sync_gamelist(self, evt):
        self.getGames()
    # LOGIN FUNCTIONS
    # -------------------------
    def login(self, name, passwd):
        log.debug("Initiated login")
        self.send("INITLOGIN", name)
        self.passwd = passwd
    
    @expose('CHALLENGE')
    def onChallenge(self, evt):
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
    def loginSuccess(self, args):
        actions.emmit_action('login', True)
    
    @expose('LOGINF')
    def loginFailure(self, args):
        actions.emmit_action('login', False)
    # LOGIN FUNCTIONS END
    # -------------------------
    
    # USER WIZARD FUNCTIONS
    # -------------------------
    def nameAvailability(self, name):
        self.send("NAMEAVAIL", name)
        log.debug("Sent NAMEAVAIL")
    
    def emailAvailability(self, email):
        self.send("EMAILAVAIL", email)
        
        log.debug("Sent EMAILAVAIL")
        
    @expose('EMAILUNAVAIL')
    def onEmailUnAvailable(self, evt):
        actions.emmit_action('email_available', False)
    
    @expose('EMAILAVAIL')
    def onEmailAvailable(self, evt):
        actions.emmit_action('email_available', True)
    
    @expose('NAMEUNAVAIL')
    def onNameUnAvailable(self, evt):
        actions.emmit_action('name_available', False)

    @expose('NAMEAVAIL')
    def onNameAvailable(self, evt):
        actions.emmit_action('name_available', True)
    # USER WIZARD FUNCTIONS END
    # -------------------------

    def closeGame(self):
        self.send("CLOSEGAME")
    
    @expose('GAMEFULL')
    def onGameFull(self, evt):
        pass
    
    @expose('NOSUCHGAME')
    def noSuchGame(self, evt):
        self.getGames() # To synchronize the gamelist again
    
    def onAny(self, evt):
        log.warn("Received unknown event\n"
                      "Keyword: %s\n" 
                      "Arguments: %s" % (evt.keyword,
                                         evt.arg_list
                                         )
                      )
    def connectionLost(self, reason):
        log.warn("Connection to server lost")
    
    @expose('CONNLOST')
    def onConnLost(self, evt):
        actions.emmit_action('conn_lost')
    
    @expose('WON')
    def onWon(self, evt):
        actions.emmit_action('game_over', ID_WIN)
    
    @expose('LOST')
    def onLost(self, evt):
        actions.emmit_action('game_over', ID_LOST)
    
    @expose('JOINEDGAME')
    def joined(self, evt):
        pass

    def hostGame(self, name, ranked=False):
        log.debug("HOSTGAME %s %s" % (name, ranked))
        self.send("HOSTGAME", (name, int(ranked)))

    def getGames(self):
        self.send("GETGAMES")
    
    @expose('GAMES')
    def onGames(self, evt):
        games = evt.arg_list
        r_games = []
        for game in games:
            if game:
                id, name, player, score, full, ranked = game
                if name.strip() != "":
                    r_games.append(GameInfo(str(id), name, player, str(score), 
                                            full, ranked, self))
        actions.emmit_action('gamelist', r_games)

    def joinGame(self, id):
        self.send("JOINGAME", id)
        
    @expose('INGAME')
    def onInGame(self, evt):
        log.warn("Already in a room")
        actions.emmit_action('in_game')

    def onID(self, evt):
        self.id = int(evt.arg)
        tell_gui("ID %d" % self.id)
    
    @expose('START')
    def onStart(self, evt):
        log.info("Game started")
        self.active = False
        actions.emmit_action('start', False)
    
    @expose('NOTYOURTURN')
    def onNotTurn(self, evt):
        log.warn("Not your turn!")
        if self.active:
            log.error("Client self.active wrong!")
            self.active = False
        else:
            log.error("Server does not accept client turn although "
                      "self.active = True at the client")
    
    def doTurn(self, field, row, position, rot_dir, rot_field):
        if self.active:
            self.send("DOTURN", (str(field), str(row), str(position), rot_dir, 
                                 rot_field))
            self.active = False
        
    @expose('YOURTURN')
    def onTurn(self, evt):
        log.debug("Received TURN %s " % str(evt.arg_list))
        field, row, position, rot_dir, rot_field = evt.arg_list
        actions.emmit_action('turn_recv', evt.arg_list)
        self.active = True
    
    @expose('BEGIN')
    def onBegin(self, evt):
        log.debug("Received BEGIN")
        self.active = True
        actions.emmit_action('start', True)
    
    @expose('BYE')
    def onBye(self, evt):
        self.stop()
        
    @expose('REGISTERED')
    def registered(self, evt):
        pass


def runClient(host, port):
    from twisted.internet import reactor, protocol
    f = protocol.ClientFactory()
    f.protocol = Conn
    f.clients = []
    reactor.connectTCP(host, port, f)


if __name__ == '__main__':
    test = Conn()
    print test.binds.keys()
