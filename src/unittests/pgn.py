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
from random import choice, randint
from pypentago.pgn import *
from os import remove

def get_temp_filename():
    """ Get a temp filename for the unittest """
    import tempfile
    temp_file = tempfile.NamedTemporaryFile()
    temp_file_name = temp_file.name
    temp_file.close()
    return temp_file_name

class CheckPGN(unittest.TestCase):
    """ Check the PGN functions """
    def test_pgn(self):                    
        """ check if pgn functions are okay """
        for integer in xrange(1, 4000):
            coords = (randint(0, 2), randint(0, 2), randint(0, 2), 
                      choice(("L", "R")), randint(0, 2))
            self.assertEqual(coords, from_pgn(to_pgn(*coords)))
    def test_write_file(self):
        """ Check if writing and parsing of files is okay """
        for integer in xrange(1, 4000):
            coords = []
            for elem in xrange(randint(5, 10)):
                coords.append((randint(0, 2), randint(0, 2), randint(0, 2), 
                              choice(("L", "R")), randint(0, 2)))
            temp_file = get_temp_filename()
            write_file(coords, temp_file)
            check_coords = parse_file(temp_file)
            remove(temp_file)
            self.assertEqual(coords, check_coords)
if __name__ == "__main__":
    unittest.main()