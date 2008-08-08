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

import time
from datetime import datetime
class GameHistory(object):
    def __init__(self, winner_id, loser_id, winner_rating=0, loser_rating=0, 
                 pgn_string=None, comment_log=None):
        
        
        self.winner_id          = winner_id        
        self.winner_rating      = winner_rating


        self.loser_id          = loser_id
        self.loser_rating      = loser_rating

        
        self.pgn_string     = pgn_string
        self.comment_log    = comment_log
        self.time_stamp     = datetime.utcnow()
    def test():
        pass
    def __repr__(self):
        str_repr = str((self.winner_id, self.loser_id, self.winner_rating, 
                        self.loser_rating, self.comment_log))  
        return "<GameHistory(%s)>" % str_repr
        
