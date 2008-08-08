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

from datetime import datetime
import time
class Player(object):
    def __init__(self, player_name, passwd_hash, real_name, 
                 player_email, player_profile=None, current_rating=1400):
        
        
        self.player_name        = player_name
        self.passwd_hash        = passwd_hash
        self.real_name          = real_name
        self.player_email       = player_email   
        self.date_registered    = datetime.utcnow()                
        self.current_rating     = current_rating
        self.player_profile     = player_profile
        
    
    def __cmp__(self, other):
        
        if None == other:
            return -1
        if not isinstance(other, Player):
            return cmp(self, other)
        
        
        retval = (cmp(self.player_name, other.player_name)
               + cmp(self.passwd_hash, other.passwd_hash) 
               + cmp(self.real_name, other.real_name)
               + cmp(self.player_email, other.player_email)
               + cmp(self.date_registered, other.date_registered)
               + cmp(self.current_rating, other.current_rating)
               + cmp(self.player_profile, other.player_profile)
               + cmp(self.date_registered, other.date_registered))
        
        return cmp(0, retval)
        
         
        
        
    def __repr__(self):
        str_repr = str((self.player_name, self.passwd_hash, self.real_name, 
                        self.player_email, self.date_registered, 
                        self.player_profile, self.current_rating))
        return "<Player(%s)>" % str_repr
