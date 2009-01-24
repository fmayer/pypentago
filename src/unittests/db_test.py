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


from __future__ import with_statement

# Fix the PYTHONPATH so we needn't have src in it.
import sys
from os.path import dirname, abspath, join
sys.path.append(abspath(join(dirname(__file__), "..")))
# End of prefix for executable files.

import unittest
from sqlalchemy.orm import clear_mappers
from pypentago.server.db import Database, PentagoDatabase
from pypentago.server.db.dbobjs import Player
from pypentago.exceptions import NotInDB

class TestPentagoDB(unittest.TestCase):
    def setUp(self):
        self.database = PentagoDatabase('sqlite:///:memory:')
    
    def tearDown(self):
        for table in self.database.tables:
            table.drop()
        clear_mappers()
    
    def test_eq(self):
        p = Player('hitchhiker', '42', 'Douglas Adams',
                   'douglas@42.com')
        p2 = Player('hitchhiker', '42', 'Douglas Adams',
                   'douglas@42.com')
        p3 = Player('hitchhiker', '42', 'Arthur Dent',
                   'douglas@42.com')
        self.assertEqual(p, p2)
        self.assertNotEqual(p, p3)
    
    def test_insert(self):
        p = Player('hitchhiker', '42', 'Douglas Adams',
                   'douglas@42.com')
        with self.database.transaction as session:
            session.save(p)
        self.assertEquals(p, self.database.player_by_login('hitchhiker'))


if __name__ == "__main__":
    unittest.main()
