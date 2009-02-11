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
import os
import pypentago

from PyQt4 import QtGui, QtCore

from pypentago.client.connection import ClientConnection
from pypentago.client.interface.game import GameWindow
from pypentago.client.interface.server import (
    ServerWindow, ConnectDialog, RegisterDialog
)
from pypentago import core, parse_ip

servers = []


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        self.setWindowTitle("Python Pentago")
        
        connect = QtGui.QAction('&Connect', self)
        connect.setShortcut('Ctrl+O')
        connect.setStatusTip('Connect to server')
        self.connect(connect, QtCore.SIGNAL('triggered()'),
                     self.connect_to)
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(connect)
    
    def connect_to(self):
        dia = ConnectDialog()
        dia.exec_()
        server = dia.server.text()
        user = dia.user.text() or None
        pwd = dia.passwd.text() or None
        g = ServerWindow.from_string(server, user, pwd)
        g.show()


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
    from twisted.internet import reactor
    # print reactor
    main = MainWindow()
    main.show()
    reactor.run()
    app.exec_()
    return 
    game = core.Game()
    p_1 = core.PlayerData('Player 1', game)
    p_2 = core.PlayerData('Player 2', game)
    dt = GameWindow(p_1)
    ot = GameWindow(p_2)
    dt.show()
    ot.show()
    b = game.random_beginner()
    b.display_msg('System', 'You have been chosen as the beginner')
    app.exec_()
