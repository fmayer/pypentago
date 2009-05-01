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
from pypentago import core
from pypentago.util import parse_ip
from pypentago.client.core import LocalPlayer

servers = []


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        
        self.setWindowTitle("Python Pentago")
        self.setWindowIcon(
            QtGui.QIcon(pypentago.data['icon.png'])
        )
        
        connect = QtGui.QAction('&Connect', self)
        connect.setShortcut('Ctrl+O')
        connect.setStatusTip('Connect to server')
        self.connect(connect, QtCore.SIGNAL('triggered()'),
                     self.connect_to)
        
        hotseat = QtGui.QAction('&Hotseat', self)
        hotseat.setShortcut('Ctrl+H')
        hotseat.setStatusTip('Play a local hotseat game')
        self.connect(hotseat, QtCore.SIGNAL('triggered()'),
                     self.local_game)
        
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(connect)
        file_menu.addAction(hotseat)
        
        self.windows = []
    
    def connect_to(self):
        dia = ConnectDialog()
        if dia.exec_():
            server = dia.server.text()
            user = dia.user.text() or None
            pwd = dia.passwd.text() or None
            g = ServerWindow.from_string(server, user, pwd)
            g.show()
            self.windows.append(g)
    
    def local_game(self):
        game = core.Game()
        p_1 = LocalPlayer()
        p_2 = LocalPlayer()
        game.add_player(p_1)
        game.add_player(p_2)
        game.random_beginner()
        w1 = GameWindow(p_1)
        w2 = GameWindow(p_2)
        
        w1.show()
        w2.show()
        
        self.windows.append(w1)
        self.windows.append(w2)


def main(default_servers=[]):
    """ If default_servers is set the GUI automatically connects to any
    servers that it contains, opening ServerWindows for each of them. """
    app = QtGui.QApplication(sys.argv)
    from pypentago.network import qt4reactor
    qt4reactor.install(app)
    from twisted.internet import reactor
    main = MainWindow()
    main.show()
    for server in default_servers:
        g = ServerWindow.from_string(server.address, server.user,
                                     server.password)
        g.show()
        main.windows.append(g)
    reactor.run()
