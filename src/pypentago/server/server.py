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

import logging
import re

from twisted.internet import protocol, reactor
from os.path import join, split

from easy_twisted.server import startServer
from easy_twisted.async import Server

from pypentago import EMAIL_REGEX
from pypentago.server.connection import Conn
from pypentago.exceptions import NoSuchRoom
from pypentago.server import db

class Factory(protocol.ServerFactory):
    def __init__(self, database):
        self.games = {}
        self.clients = []
        self.rooms = []
        self.email_regex = re.compile(EMAIL_REGEX, re.IGNORECASE)
        self.next_id = -1
        self.database = database
        self.protocol = Conn
    
    def next_game_id(self):
        self.next_id += 1
        return self.next_id
    
    def get_room(self, name):
        for room in self.rooms:
            if room.name == name:
                return room
        raise NoSuchRoom


def run_server(port=26500, connect_string='sqlite:///:memory:'):
    log = logging.getLogger("pypentago.server")
    database = db.PentagoDatabase(connect_string)
    factory = Factory(database)
    log.info("Started server on port %d" % port)
    reactor.listenTCP(port, factory)
    reactor.run()


if __name__ == "__main__":
    print "Please run main.py to run the server"
    #runServer()
