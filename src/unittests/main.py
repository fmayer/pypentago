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

from itertools import chain

MODULES = ['core_test', 'pgn_test', 'actions_test', 'crypto_test', 'field_test']

mod = map(__import__, MODULES)

if __name__ == '__main__':
    test_cases = chain(*[unittest.findTestCases(mod) for mod in mod])
    suite = unittest.TestSuite(test_cases)
    display = unittest.TextTestRunner()
    display.run(suite)
