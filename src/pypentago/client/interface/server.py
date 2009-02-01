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
from PyQt4 import QtGui, QtCore

from pypentago.client.connection import ClientConnection
from pypentago.client.interface.game import GameWindow
from pypentago import DEFAULT_PORT


def modal_buttons(ok_label='Okay', cancel_label='Cancel'):
    """ Return ok, cancel, layout.
    
    ok and cancel are the button objects in layout.
    """
    lay = QtGui.QHBoxLayout()
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


class ServerWindow(QtGui.QMainWindow):
    def __init__(self, host, port, login_user=None, login_pwd=None):
        QtGui.QMainWindow.__init__(self)
        
        self.login_user = login_user
        self.login_pwd = login_pwd
        
        self.connection = None
        self.attempts = 5
        
        disconnect = QtGui.QAction('&Disconnect', self)
        disconnect.setShortcut('Ctrl+Q')
        disconnect.setStatusTip('Disconnect from server')
        self.connect(disconnect, QtCore.SIGNAL('triggered()'),
                     QtCore.SLOT('disconnect()'))
        
        new_game = QtGui.QAction('&New Game', self)
        new_game.setShortcut('Ctrl+N')
        new_game.setStatusTip('Open a new game')
        self.connect(new_game, QtCore.SIGNAL('triggered()'),
                     QtCore.SLOT('new_game()'))
        
        join_game = QtGui.QAction('&Join Game', self)
        join_game.setShortcut('Ctrl+J')
        join_game.setStatusTip('Join a game.')
        self.connect(join_game, QtCore.SIGNAL('triggered()'),
                     QtCore.SLOT('join_game()'))
        
        settings = QtGui.QAction('&Settings', self)
        settings.setStatusTip('Adjust settings')
        self.connect(new_game, QtCore.SIGNAL('triggered()'),
                     QtCore.SLOT('settings()'))
        
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(new_game)
        file_menu.addAction(join_game)
        file_menu.addSeparator()
        file_menu.addAction(disconnect)
        
        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(settings)
        
        self.need_connected = [disconnect]
        for widg in self.need_connected:
            widg.setEnabled(False)
        self.init_conn(host, port)
    
    def init_conn(self, host, port):
        ClientConnection.start_new(host, port, self, self.connected)
    
    @classmethod
    def from_string(cls, string, login_user=None, login_pwd=None):
        h = string.split(':')
        if len(h) == 1:
            return cls(string, DEFAULT_PORT, login_user, login_pwd)
        elif len(h) == 2:
            return cls(h[0], h[1], login_user, login_pwd)
        else:
            raise ValueError("Cannot interpret %r as server connect string!"
                             % string)
    
    def connected(self, conn):
        if self.login_user and self.login_pwd:
            conn.authenticate(self.login_user, self.login_pwd)
        self.connection = conn
        self.statusBar().showMessage("Connection to server established", 10000)
        for widg in self.need_connected:
            widg.setEnabled(True)
    
    @QtCore.pyqtSignature('')
    def disconnect(self):
        self.close()
    
    @QtCore.pyqtSignature('')
    def new_game(self):
        pass
    
    @QtCore.pyqtSignature('')
    def settings(self):
        pass
    
    @QtCore.pyqtSignature('')
    def join_game(self):
        pass
    
    def show_game(self, game):
        g = GameWindow(game)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    s = ServerWindow(0, 0)
    s.show()
    app.exec_()
