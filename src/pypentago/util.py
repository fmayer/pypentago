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

import itertools

class IDPool(object):
    def __init__(self):
        self.ids = itertools.count()
        self.free_ids = []
    
    def get(self):
        """ Return a new integer that is unique in this pool until
        it is released. """
        if self.free_ids:
            return self.free_ids.pop()
        else:
            return self.ids.next()
    
    def release(self, id_):
        """ Release the id. It can now be returned by get again. """
        self.free_ids.append(id_)


def parse_ipv4(string, default_port=-1):
    h = string.split(':')
    if len(h) == 1:
        return string, default_port
    elif len(h) == 2:
        return h[0], int(h[1])
    else:
        raise ValueError("Cannot interpret %r as IPv4 address!" % string)


def parse_ipv6(string, default_port=-1):
    if '[' in string and ']' in string:
        h = string.split(']:')
        if len(h) == 1:
            return string[1: -1], default_port
        else:
            return h[0][1:], int(h[1])
    elif not '[' in string and not ']' in string:
        return string, default_port
    else:
        raise ValueError("Cannot interpret %r as IPv6 address!" % string)


def parse_ip(string, default_port=-1):
    """ Return (host, port) from input string. This tries to automatically
    determine whether the address is IPv4 or IPv6.
    
    If not port is found default_port, which defaults to
    pypentago.DEFAULT_PORT is used.
    
    >>> parse_ip('127.0.0.1:1234')
    ('127.0.0.1', 1234)
    >>> parse_ip('[2001:0db8:85a3:08d3:1319:8a2e:0370:7344]:443')
    ('2001:0db8:85a3:08d3:1319:8a2e:0370:7344', 443)
    """
    if string.count(':') > 1:
        return parse_ipv6(string, default_port)
    else:
        return parse_ipv4(string, default_port)
