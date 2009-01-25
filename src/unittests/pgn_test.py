#! /usr/bin/env python
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


import unittest
import tempfile

from itertools import imap

from random import choice, randint, sample

from pypentago.pgn import *
from pypentago.exceptions import InvalidPGN
from pypentago import CW, CCW

def random_turn():
    r = lambda: randint(0, 2)
    return r(), r(), r(), choice(("L", "R")), r()

class CheckPGN(unittest.TestCase):
    """ Check the PGN functions """
    all_turns = [(a, b, c, d) for a in xrange(3) for b in xrange(3)
                              for c in xrange(3) for d in xrange(3)]
    def test_pgn(self):                    
        """ check if pgn functions are okay """
        for coords in self.all_turns:
            for direction in [CW, CCW]:
                c = coords[:-1] + (direction, ) + coords[-1:]
                self.assertEqual(c, from_pgn(to_pgn(*c)))

    def test_write_file(self):
        """ Check if writing and parsing of files is okay """
        for integer in xrange(1, 4000):
            game = sample(self.all_turns, randint(5, 10))
            game = [t[:-1] + (choice((CW, CCW)), ) + t[-1:] for t in game]
            temp_file = tempfile.NamedTemporaryFile()
            write_file(game, temp_file.name)
            check_coords = parse_file(temp_file.name)
            self.assertEqual(game, check_coords)
    
    def test_too_short(self):
        self.assertRaises(InvalidPGN, from_pgn, 'Aa1L')
    
    def test_too_long(self):
        self.assertRaises(InvalidPGN, from_pgn, 'Aa1RBX')
    
    def test_out_of_range(self):
        self.assertRaises(InvalidPGN, from_pgn, 'Xa1RB')

if __name__ == "__main__":
    unittest.main()
