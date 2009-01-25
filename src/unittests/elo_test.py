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

from pypentago import elo

class ELOKnownValues(unittest.TestCase):
    def setUp(self):
        # WHEN ADDING DATA ALWAYS PROVIDE SOURCES
        self.known_values = (
            # DATA FROM GERMAN WIKIPEDIA 
            # See http://tinyurl.com/2b3dku
            ((2577, 2806), (2585, 2798)), 
            ((2806, 2577), (2808, 2575)),
            ((2806, 2577, True), (2803, 2580)), # DRAW
        )
    
    def test_known_values(self):
        for key, value in self.known_values:
            self.assertEqual(elo.get_new_rating(*key), value)
