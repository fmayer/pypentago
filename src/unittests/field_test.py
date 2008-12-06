#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pyPentago - a board game
# Copyright (C) 2008 Florian Mayer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
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

from itertools import permutations, imap
from copy import deepcopy
from random import randint

from pypentago.server import field
from pypentago.exceptions import SquareNotEmpty

class CheckServerField(unittest.TestCase):
    """ Check the pypentago.server.field.Field methods """
    def test_rotate(self):                    
        """ check if rotation methods are okay """
        for coords in imap(list, permutations([0,1,2], 3)):
            old_field = field.Field()
            rot_field = coords[0]
            old_field.set_stone(1, *coords)
            new_field = deepcopy(old_field)
            new_field.rotleft(rot_field)
            new_field.rotright(rot_field)
            self.assertEqual(str(old_field), str(new_field))
    
    def test_set_stone_exception(self):
        """ check if exception is raised when attempting to set a piece onto a 
        square where there already is one """
        for coords in imap(list, permutations([0,1,2], 3)):
            old_field = field.Field()
            old_field.set_stone(1, *coords)
            args = [1] + coords
            self.assertRaises(SquareNotEmpty, old_field.set_stone, 
                              *args)

if __name__ == "__main__":
    unittest.main()
