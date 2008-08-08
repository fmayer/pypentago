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

from pypentago.server.glicko2 import RatingCalculator
import unittest

#
#Test module for the glicko2 function
#still developing this, its just a start
#


class Glicko2Test(unittest.TestCase):

    def setUp(self):
        self.rc = RatingCalculator()

    def test_g(self):
        result = self.rc._RatingCalculator__g(1.7269)
        self.assertEqual(0.72419999999999995,result)

    def runTest(self):
        self.setUp()
        self.test_g()
        pass

if __name__ == '__main__':
    unittest.main()
