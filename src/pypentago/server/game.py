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

import logging

from random import choice

from pygrade import elo

from pypentago import pgn
from pypentago.server import field

from pypentago.server import db
from pypentago.server.db.dbobjs import GameHistory

class Game(object):
    def __init__(self, player, name, ranked=False):
        self.log = logging.getLogger("pypentago.game")
        self.name = name
        self.ranked = ranked
        self.players = []
        self.server = player.server
        self.join(player)
        self.field = field.Field()
        self.turn_log = []
        for player in self.players:
            player.game = self
        self.sync_game_lists()

    def sync_game_lists(self):
        """ To be executed every time a game is opened or closed.
        Keeps all players' gamelists synchronised """
        for client in self.server.clients:
            client.send("SYNCGAMES")

    def send_all(self, msg):
        for player in self.players:
            player.send(msg)

    def join(self, conn):
        self.log.debug("[joinGame]")
        if not self.full:
            self.players.append(conn)
            conn.game = self
        else:
            return False
        if len(self.players) == 2:
            self.start()

    def close(self):
        self.log.debug("[game.close]")
        for player in self.players:
            self.players.remove(player)
            player.game = False
            #self.opponent.send("CONNLOST")
            player.opponent = None
        if self in self.server.games:
            self.server.games.remove(self)
        else:
            self.log.warn("[Game not in gamelist!]")
        self.log.debug("Games " + str(self.server.games))
        self.sync_game_lists()
        del self

    def switch_active_player(self, arg):
        for player in self.players:
            if player.active:
                player.active = False
            else:
                player.active = True
                player.send("YOURTURN", arg)

    def get_active_player(self):
        for player in self.players:
            if player.active:
                return player

    def set_active_player(self, plr):
        plr.active = True
        plr.opponent.active = False

    def applyturn(self, player, field, row, position, rot_dir, rot_field):
        if player.active:
            self.turn_log.append((field, row, position, rot_dir, 
                                 rot_field))
            self.log.debug("player active")
            self.field.applyturn(
                int(player.game_id), int(field), 
                int(row), int(position), rot_dir, int(rot_field)
            )
            self.switch_active_player((field, 
                                       row, position, 
                                       rot_dir, rot_field))
        else:
            self.log.error("Player %d sent although "
                           "it's player %d turn" % (player.game_id, 
                                                    self.active_player.game_id))

            player.send("NOTYOURTURN")
        self.log.debug("Field: \n" + str(self.field))
        self.won()

    def start(self):
        self.tell_opponent()	
        self.choose_random_beginner()

    def choose_random_beginner(self):
        self.active_player = choice(self.players)
        self.active_player.active = True
        self.active_player.game_id = 1
        self.active_player.opponent.game_id = 2
        self.active_player.opponent.active = False
        self.active_player.send("BEGIN")
        self.active_player.opponent.send("START")

    def send_id(self):
        for player in self.players:
            player.send("ID %d" % player.game_id)

    def tell_opponent(self):
        self.players[0].opponent = self.players[1]
        self.players[1].opponent = self.players[0]

    def won(self):
        won = self.field.won()
        self.log.debug("WON: %s" % won)
        if won:
            self.log.debug("Game has been WON")
            for player in self.players:
                if player.game_id == won:
                    player.send("WON")
                    self.log.debug("[sent WON]")
                    player_won = player
                else:
                    player.send("LOST")
                    self.log.debug("[sent LOST]")
                    player_lost = player
            if self.ranked:
                self.report_game(player_won, player_lost)
            self.game_over(player_won, player_lost)
            for player in self.players:
                player.leave_game()

    def game_over(self, winner, loser):
        winner_db = winner.database_player
        loser_db = loser.database_player
        with db.transaction() as session:
            session.save(
                GameHistory(winner_db.player_id, 
                            loser_db.player_id,
                            winner_db.current_rating,
                            loser_db.current_rating,
                            pgn.get_game_pgn(self.turn_log)
                            )
                )

    def report_game(self, winner, loser):
        winner_db = winner.database_player
        loser_db = loser.database_player
        self.log.debug("Importing ELO module")
        winner_rating = winner_db.current_rating
        loser_rating = loser_db.current_rating

        self.log.debug("Updating rating attributes for both players")
        winner_db.current_rating, loser_db.current_rating = (
            elo.get_new_rating(winner_rating, loser_rating))
        self.log.debug("Updating database")
        winner.write_to_database()
        loser.write_to_database()

    def get_amount_of_players(self):
        return len(self.players)

    def get_full(self):
        if len(self.players) == 2:
            return True
        else:
            return False
    
    full = property(fget=get_full)
    player_amount = property(get_amount_of_players)
    active_player = property(get_active_player, set_active_player)
