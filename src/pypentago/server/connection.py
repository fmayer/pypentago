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
from pypentago.server.game import Game
from pypentago.get_conf import get_conf_obj
from pypentago.server import db
from pypentago.server.mailing import Email
from pypentago.server.db.dbobjs import Player
from pypentago.exceptions import NoSuchRoom, NotInDB

from easy_twisted.server import Connection
from easy_twisted.connection import expose


conf = get_conf_obj('server')

email_text = ("Dear %(real_name)s,\n"
              "Thank you for registering with pypentago.\n"
              "Your verification code is %(code)s. \n"
              "Please use the "
              "\"Activate Account\" dialog for activating your account.\n"
              "\n"
              "Please note that it is forbidden to register multiple "
              "accounts for one person.")


def get_rand_str():
    # Variable lenght of random string for improved security:
    lenght = randint(13, 18)
    return "".join((choice(ascii_letters) for elem in range(lenght)))


class Conn(Connection):
    def construct(self):
        self.context = actions.Context()
        actions.ActionHandler.__init__(self, self.context)
    
    def init(self):
        self.log = logging.getLogger("pypentago.connection")
        self.log.info("Got connection from %s" % self.transport.getPeer().host)
        
        self.server = self.factory
        self.logged_in = False
        self.name = "Player"
        self.game_id = None
        self.game = None
        self.opponent = None
        self.active = False

    @expose('CHPWD')
    def change_passwd(self, evt):
        """ Change the password in the database. The event has to provide the 
        old password and the new password. If the old password matches the one 
        stored in the database, it is changed. """
        old_pwd, new_pwd = evt.arg_list
        if old_pwd == self.database_player.passwd_hash:
            self.database_player.passwd_hash = new_pwd
            try:
                self.write_to_database()
                self.send("PWDCHANGED")
            except:
                self.send("PWDNOTCHANGED")
                raise
        else:
            self.send("WRONGPWD")
    
    @expose('GETPLAYER')
    def get_player(self, evt):
        """ Get profile information of a player """
        player_login = evt.arg
        try:
            db_player = db.players_by_login(player_login)[0]
        except NotInDB:
            self.send("NOTINDB")
            return False
        arg_list = (db_player.player_name, db_player.real_name, 
                    db_player.current_rating, db_player.player_profile)
        self.send("PLAYER", arg_list)
    
    @expose('RPROTVERSION')
    def request_protocol_version(self, evt):
        """ Get the protocol version of the server """
        self.send("PROTVERSION", PROTOCOL_VERSION)
    
    @expose('PROTVERSION')
    def protocol_version(self, evt):
        """ Compare server and client protocol version """
        server_prot = int(evt.arg_list[0])
        if server_prot != PROTOCOL_VERSION:
            self.log.error("Client protocol does not match client protocol!")

    @expose('INITLOGIN')
    def init_login(self, evt):
        """
        Initializes login, generates random string to be sent to the client.
        This improves security, see http://www.hcsw.org/reading/chalresp.txt
        """
        self.log.debug("Received login initiation")
        self.temp_name = evt.arg
        self.log.debug("%s attempted to login" % self.temp_name)
        self.log.debug("Username clear of special char: %s" % \
                       (self.temp_name == self.temp_name.strip()))
        try:
            self.database_player = db.players_by_login(self.temp_name)[0]
        except NotInDB:
            self.send("LOGINF")
            return False
        if not self.database_player:
            self.send("LOGINF")
            self.temp_login = False
            return False
        passwd = self.database_player.passwd_hash
        self.log.debug(passwd)
        rand_str = get_rand_str()
        self.log.debug("Formulating challenge")
        self.temp_login = sha(rand_str+passwd).hexdigest()
        self.log.debug("Sending challenge")
        self.send("CHALLENGE", rand_str)
    
    @expose('RESPONSE')
    def on_response(self, evt):
        """ Checks if the login response matches 
        the one stored by the server """
        self.log.debug("Received response")
        data = evt.arg
        if data == self.temp_login:
            self.logged_in = True
            self.name = self.temp_name
            del self.temp_name
            del self.temp_login
            self.send("LOGINS")
            self.log.info("Player successfully logged in")
        else:
            self.send("LOGINF")
            self.log.info("Player login failed")
        
    def write_to_database(self):
        """ Write changes to self.database_player to the database """
        with db.transaction() as session:
            session.save(self.database_player)
    
    @expose('ACTIVATE')
    def activate_user(self, evt):
        """ Activate a user through a code sent via email """
        if not self.logged_in:
            self.send("NOTLOGGEDIN")
            return False
        if self.database_player.activated:
            self.send("ALREADYACTIVE")
            return True

        code = evt.arg
        if code == self.database_player.activation_code:
            self.database_player.activated = True
            self.send("ACTIVATED")
        else:
            self.send("WRONGCODE")
    
    @expose('REGISTER')
    def register_user(self, evt):
        activ_code = get_rand_str()
        name, passwd, email, profile, real_name = evt.arg_list
        if not name:
            self.send("INVALIDNAME")
            return False
        if (self.server.email_regex.match(email) and db.email_available(email)
            and db.login_available(name)):
            new_player = player.Player(name, passwd, real_name, email,
                                   player_profile=profile)
            new_player.activated = False
            new_player.activation_code = activ_code
            try:
                with db.transaction() as session:
                    session.save_player(new_player)
                self.send("REGISTERED")
                ##self.send_activation_email(real_name, email)
            except DuplicateLoginError:
                self.send("DUPNAME")
        else:
            self.log.info("%s does not match email regex" % email)
            self.send("EMAILINVALID")
    
    def send_activation_email(self, real_name, email_address):
        send_email = Email(sender, email_address, "pypentago activation", 
                           email_text % {"real_name": real_name, 
                                         "code": activ_code})
        send_email.send(conf.get('smtp', 'host'), conf.get('smtp', 'port'), 
                        conf.get('smtp', 'user'), conf.get('smtp', 'password'))
    
    @expose('NAMEAVAIL')
    def name_available(self, evt):
        self.log.debug("Received NAMEAVAIL")
        name = evt.arg
        name_available = db.login_available(name)
        if name_available:
            self.send("NAMEAVAIL")
        else:
            self.send("NAMEUNAVAIL")
    
    @expose('EMAILAVAIL')
    def email_available(self, evt):
        self.log.debug("Received EMAILAVAIL")
        email = evt.arg
        email_available = db.email_available(email)
        if email_available:
            self.send("EMAILAVAIL")
        else:
            self.send("EMAILUNAVAIL")
    
    @expose('CLOSEGAME')
    def close_game(self, evt):
        """ Closes the game that is currently opened by the user """
        self.log.debug("in close_game")
        if self.game:
            self.log.debug("close_game")
            self.game.close()
        else:
            self.log.warn("User attempted to close game although "
                          "he has none opened")
    
    @expose('PLAYERCOUNT')
    def on_player_count(self, evt):
        self.send("PLAYERCOUNT", str(len(self.server.players)))
    
    @expose('GETGAMES')
    def on_get_games(self, evt):
        self.log.debug("In getrooms")
        games = []
        for id, game in enumerate(self.server.games):
            if not game.full:
                games.append(
                    (id, game.name, game.players[0].name, 
                     game.players[0].database_player.current_rating, 
                     game.full, game.ranked)
                )

        self.send("GAMES", tuple(games))
    
    @expose('JOINGAME')
    def join_game(self, evt):
        """ Join the game with the sent id. If player is currently in a game
        it sends back INGAME. If the game with the gived id does not exist 
        NOSUCHGAME is sent back. If the game already has two players, GAMEFULL 
        is sent back. If player joined game successfully, JOINEDGAME is sent """
        if not self.logged_in:
            self.send("NOTLOGGEDIN")
            return False
        id = int(evt.arg)
        if id >= len(self.server.games):
            self.send("NOSUCHGAME", str(id))
        else:
            game = self.server.games[id]
            if self.game:
                self.send("INGAME")
            elif game.join(self):
                self.send("JOINEDGAME")
            else:
                self.send("GAMEFULL", str(id))
    
    @expose('HOSTGAME')
    def host_game(self, evt):
        """ Open a game. Event has to contain the name and whether it is ranked.
        Ranked may be 1 for ranked or 0 for not ranked. If the player already is
        in a game, INGAME is sent. """
        if not self.logged_in:
            self.send("NOTLOGGEDIN")
            return False
        name, ranked = evt.arg_list
        ranked = int(ranked)
        if not self.game:
            game = Game(self, name, ranked)
            self.server.games.append(game)
            self.game = game
        else:
            self.send("INGAME")
    
    @expose('LEAVEGAME')
    def leave_game(self, evt=None):
        """ Leave the game the player currently is in. Also closes that game """
        if self.game is not None and isinstance(self.game, Game):
            self.game.players.remove(self)
            self.game.close()
            self.game = None
        if self.opponent and isinstance(self.opponent, Conn):
            self.opponent = None
    
    def destruct(self, reason):
        """ Inform the opponent that your connection has been lost.
        Close the game the player was in if he was. """
        if self.opponent:
            self.opponent.send("CONNLOST")
        if self.game:
            if self.game.ranked:
                # The player losing connection is always considered the loser 
                # for ranking in order to prevent disconnection if losing
                self.game.report_game(self.opponent, self)
            self.game.close()
        
    def send_opponent(self, keyword, args):
        """ Send to opponent """
        self.opponent.send(keyword, args)
    
    @expose('BYE')
    def on_bye(self, evt):
        self.game.close()
    
    @expose('DOTURN')
    def on_turn(self, event):
        """ Apply turn to the server field """
        if not self.logged_in:
            self.send("NOTLOGGEDIN")
            return False            
        if not self.game:
            self.send("NOTINGAME")
            return False
        self.log.debug(str(event.arg_list))
        field, row, position, rot_dir, rot_field = event.arg_list
        if self.active:
            self.game.applyturn(self, field, row, 
                                position, rot_dir, rot_field)
    
    def on_any(self, evt=None):
        """ Called when unbound keyword is received """
        self.log.warn("Received unknown event\n"
                      "Keyword: %s\n" 
                      "Arguments: %s" % (evt.keyword, evt.arg_list)
                      )
    
    onAny = on_any
    
    def get_room(self, name):
        for room in self.factory.rooms:
            if room.name == name:
                return room
        raise NoSuchRoom
