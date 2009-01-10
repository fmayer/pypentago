#!/usr/bin/env python
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

import sys

from PyQt4 import QtGui

from pypentago.client.interface.game import GameWindow
from pypentago import core


def main(default_servers=[]):
    """ Main GUI entry-point. Currently this is for testing purposes only.
    default_servers currently has no effect at all.
    
    What it is supposed to do:
    If default_servers is set the GUI automatically connects to any servers
    that it contains, opening ServerWindows for each of them. """
    # TODO: Implement what the docstring says
    app = QtGui.QApplication(sys.argv)
    from easy_twisted import qt4reactor
    qt4reactor.install()
    game = core.Game()
    dt = GameWindow(game)
    ot = GameWindow(game)
    dt.show()
    ot.show()
    game.random_beginner()
    app.exec_()
