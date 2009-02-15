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
import optparse
import sys
import imp
import os

import twisted
import pypentago
import sqlalchemy

from itertools import chain
from pypentago import core

PATH = os.path.abspath(os.path.dirname(__file__))
MODULES = ['core_test', 'pgn_test', 'actions_test', 'crypto_test', 
           'elo_test', 'db_test']


class DummyTestRunner:
    def run(self, test):
        result = unittest.TestResult()
        test(result)
        return result


def run_all(test_runner=None, but=None):
    if but is None:
        but = []
    
    if test_runner is None:
        test_runner = DummyTestRunner()
    
    for elem in but:
        if elem.strip() in MODULES:
            MODULES.remove(elem)
    
    mod = map(__import__, MODULES)
    test_cases = chain(*[unittest.findTestCases(mod) for mod in mod])
    suite = unittest.TestSuite(test_cases)
    display = unittest.TextTestRunner()
    result = display.run(suite)
    return result


if __name__ == '__main__':
    print "os.name: %s" % os.name
    print "sys.platform: %s" % sys.platform
    print "Python: %s" % sys.version.replace('\n', '    ')
    print str(twisted.version)[1:-1].replace(', version', ':')
    print "sqlalchemy: %s" % sqlalchemy.__version__
    print "speedup: %s" % (core.EXTENSION_MODULE and 'yes' or 'no')
    print "path: %s" % os.path.abspath(os.path.dirname(pypentago.__file__))
    print 
    result = run_all(unittest.TextTestRunner(), sys.argv[1:])
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

