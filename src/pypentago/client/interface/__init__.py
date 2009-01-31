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

from pypentago.client.interface.game import GameWindow
from pypentago.client.interface.server import ServerWindow
from pypentago import core

servers = []

OK_ICON = pypentago.data['success.png']
CANCEL_ICON = pypentago.data['fail.png']

def modal_buttons(ok_label='Okay', cancel_label='Cancel'):
    """ Return ok, cancel, layout.
    
    ok and cancel are the button objects in layout.
    """
    lay = QtGui.QHBoxLayout()
    offset = 0
    ok = QtGui.QPushButton(QtGui.QIcon(OK_ICON), ok_label)
    cancel = QtGui.QPushButton(QtGui.QIcon(CANCEL_ICON), cancel_label)
    if os.name == 'nt':
        # Left-aligned, OK first.
        lay.addStretch(0)
        lay.addWidget(ok)
        lay.addWidget(cancel)
    else:
        # Right-aligned, Cancel first.
        lay.addStretch(1)
        lay.addWidget(cancel)
        lay.addWidget(ok)
    return ok, cancel, lay


class ConnectDialog(QtGui.QDialog):
    """ Dialog to get connection and login information.
    
    >>> d = ConnectDialog()
    >>> if d.show():
    ...     user = d.user.text()
    ...     passwd = d.passwd.text()
    ...     server = d.server.text()
    >>>
    """
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setModal(True)
        self.setWindowTitle('Python Pentago - Login')
        
        self.server = QtGui.QLineEdit()
        self.user = QtGui.QLineEdit()
        self.passwd = QtGui.QLineEdit()
        self.passwd.setEchoMode(QtGui.QLineEdit.Password)
        
        grid = QtGui.QGridLayout()
        
        layout = [
            (QtGui.QLabel('Server:'), self.server),
            (QtGui.QLabel('User:'), self.user),
            (QtGui.QLabel('Password:'), self.passwd),
        ]
        for i, elem in enumerate(layout):
            for j, widg in enumerate(elem):
                grid.addWidget(widg, i, j)
        
        ok, cancel, lay = modal_buttons()
        register = QtGui.QPushButton('Register')
        
        self.connect(ok, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('accept()'))
        self.connect(cancel, QtCore.SIGNAL('clicked()'),
                     self, QtCore.SLOT('reject()'))
        
        button_line = QtGui.QHBoxLayout()
        button_line.addWidget(register)
        # FIXME: Use following code and figure out how to insert
        # icons and how not to localise the buttons to the OS.
        # but = QtGui.QDialogButtonBox()
        # but.addButton(QtGui.QDialogButtonBox.Ok)
        # but.addButton(QtGui.QDialogButtonBox.Cancel)
        button_line.addLayout(lay)
        
        main = QtGui.QVBoxLayout()
        main.addLayout(grid)
        main.addLayout(button_line)
        # Align all widget on the top.
        main.addStretch(1)
        
        self.setLayout(main)


class RegisterDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setModal(True)
        
        grid = QtGui.QGridLayout()
        
        self.user = QtGui.QLineEdit()
        self.passwd = QtGui.QLineEdit()
        self.passwd.setEchoMode(QtGui.QLineEdit.Password)
        self.real_name = QtGui.QLineEdit()
        self.email = QtGui.QLineEdit()
        
        ok, cancel, but = modal_buttons()
        self.connect(ok, QtCore.SIGNAL('clicked()'),
            self, QtCore.SLOT('accept()'))
        self.connect(cancel, QtCore.SIGNAL('clicked()'),
            self, QtCore.SLOT('reject()'))
        # FIXME: Use following code and figure out how to insert
        # icons and how not to localise the buttons to the OS.
        # but = QtGui.QDialogButtonBox()
        # but.addButton(QtGui.QDialogButtonBox.Ok)
        # but.addButton(QtGui.QDialogButtonBox.Cancel)
        
        layout = [
            (QtGui.QLabel('Username:'), self.user),
            (QtGui.QLabel('Password:'), self.passwd),
            (QtGui.QLabel('Real Name:'), self.real_name),
            (QtGui.QLabel('Email:'), self.email),
        ]
        for i, elem in enumerate(layout):
            for j, widg in enumerate(elem):
                grid.addWidget(widg, i, j)
        
        main = QtGui.QVBoxLayout()
        main.addLayout(grid)
        main.addWidget(but)
        main.addStretch(1)
        self.setLayout(main)


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow(self)
        
        self.setWindowTitle("Python Pentago")
        
        connect = QtGui.QAction('&Disconnect', self)
        connect.setShortcut('Ctrl+Q')
        connect.setStatusTip('Disconnect from server')
        self.connect(connect, QtCore.SIGNAL('triggered()'),
                     QtCore.SLOT('connect()'))


def main(default_servers=[]):
    """ Main GUI entry-point. Currently this is for testing purposes only.
    default_servers currently has no effect at all.
    
    What it is supposed to do:
    If default_servers is set the GUI automatically connects to any servers
    that it contains, opening ServerWindows for each of them. """
    # TODO: Implement what the docstring says
    app = QtGui.QApplication(sys.argv)
    # We don't need that until we implement network games:
    # from easy_twisted import qt4reactor
    # qt4reactor.install()
    game = core.Game()
    dt = GameWindow(game)
    ot = GameWindow(game)
    dt.show()
    ot.show()
    b = game.random_beginner()
    b.display_msg('System', 'You have been chosen as the beginner')
    app.exec_()
