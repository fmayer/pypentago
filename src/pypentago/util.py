# -*- coding: us-ascii -*-

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


class IDPool(object):
    """
    Pool that returns unique identifiers.
    
    Identifierers obtained using the get method are guaranteed to not be
    returned by it again until they are released using the release method.
    
        >>> pool = IDPool()
        >>> pool.get()
        0
        >>> pool.get()
        1
        >>> pool.get()
        2
        >>> pool.release(1)
        >>> pool.get()
        1
        >>> 
    """
    def __init__(self):
        self.max_id = -1
        self.free_ids = []
    
    def get(self):
        """ Return a new integer that is unique in this pool until
        it is released. """
        if self.free_ids:
            return self.free_ids.pop()
        else:
            self.max_id += 1
            return self.max_id
    
    def release(self, id_):
        """ Release the id. It can now be returned by get again.
        
        Will reset the IDPool if the last id in use is released. """
        self.free_ids.append(id_)
        if len(self.free_ids) == self.max_id + 1:
            self.reset()
    
    def reset(self):
        """ Reset the state of the IDPool. This should only be called when
        no identifier is in use. """
        self.max_id = -1
        self.free_ids = []


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
    
    If no port is found default_port, which defaults to -1 is used.
    
    >>> parse_ip('127.0.0.1:1234')
    ('127.0.0.1', 1234)
    >>> parse_ip('[2001:0db8:85a3:08d3:1319:8a2e:0370:7344]:443')
    ('2001:0db8:85a3:08d3:1319:8a2e:0370:7344', 443)
    """
    if string.count(':') > 1:
        return parse_ipv6(string, default_port)
    else:
        return parse_ipv4(string, default_port)

def offset(quad):
    """ Offset of quadrant from (0/0) in (rows, cols). """
    return (3 * (quad >= 2), 3 * (quad == 1 or quad == 3))

def absolute(quad, row, col):
    """ Return absolute coordinates of row, col relative to quad. """
    roff, coff = offset(quad)
    arow = roff + row
    acol = coff + col
    return arow, acol

def contains(row, col):
    """ Return which quadrant contains the position at (row, col). """
    r = 0
    if row > 2:
        r += 2
    if col > 2:
        r += 1
    return r
