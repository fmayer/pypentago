# easy_twisted - a framework to easily use twisted
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


#: Used when an Event has not been handled
BIND_ANY = ("any", "keyword")


class NoBindAvailable(Exception):
    pass


class Event(object):
    """
    This class represents an incoming either triggered by a bound text-keyword 
    or by BIND_ANY.

    Contains:
        - B{keyword} - I{The keyword that triggered the event}
        - B{parent} - I{The connection that received the connection}
        - B{arg} - I{Everything received but the keyword}
        - B{arg_list} - I{List of arguments}
    """
    def __init__(self, parent, keyword, data):
        self.keyword = keyword
        self.parent = parent
        self.arg = data
        self.arg_list = data
    
    def raise_event(self):
        """ Raise the event """
        if self.parent.context.actions[self.keyword]:
            self.parent.context.emmit_action(self.keyword, self)
        elif self.parent.context.actions[BIND_ANY]:
            self.parent.context.emmit_action(BIND_ANY, self)
        elif hasattr(self.parent, 'onAny'):
            self.parent.onAny(self)
        else:
            raise NoBindAvailable
            

