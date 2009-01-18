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

from core import DatabaseObject
from datetime import datetime

class Player(DatabaseObject):
    def __init__(self, player_name, passwd_hash, real_name, 
                 player_email, player_profile=None, current_rating=1400):
        DatabaseObject.__init__(self, locals())


class GameHistory(DatabaseObject):
    def __init__(self, winner_id, loser_id, winner_rating=0, loser_rating=0, 
                 pgn_string=None, comment_log=None):
        DatabaseObject.__init__(self, locals())
        self.time_stamp = datetime.now()
