#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

# Prefix any executable file with this to set the correct PYTHONPATH:
import sys
from os.path import dirname, abspath, join
script_path = dirname(__file__)
sys.path.append(abspath(join(script_path, ".."))) # Adjust to number
                                            # of subdirs the current
                                            # file is in.
# End of prefix for executable files.
import unittest
import tempfile

from itertools import permutations, imap

from random import choice, randint, sample

from pypentago.pgn import *
from pypentago import CW, CCW

def random_turn():
    r = lambda: randint(0, 2)
    return r(), r(), r(), choice(("L", "R")), r()

class CheckPGN(unittest.TestCase):
    """ Check the PGN functions """
    all_turns = tuple(permutations([0,1,2] * 4, 4))
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


if __name__ == "__main__":
    unittest.main()
