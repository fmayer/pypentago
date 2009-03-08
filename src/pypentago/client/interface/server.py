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

from PyQt4 import QtGui, QtCore

from pypentago.client.core import LocalPlayer
from pypentago.client.connection import ClientConnection
from pypentago.client.interface.game import GameWindow
from pypentago import DEFAULT_PORT, data
from pypentago.util import parse_ip


OK_ICON = data['success.png']
CANCEL_ICON = data['fail.png']


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


class GameList(QtGui.QWidget):
    def __init__(self, join):
        QtGui.QWidget.__init__(self)
        self.data = []
        self.join = join
        self.gamelist = QtGui.QListWidget()
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.gamelist)
        self.setLayout(layout)
        self.connect(
            self.gamelist,
            QtCore.SIGNAL("itemDoubleClicked ( QListWidgetItem * )"),
            self.select_item
        )
    
    def clear(self):
        self.data = []
        self.gamelist.clear()
    
    def select_item(self, item):
        indx = self.gamelist.indexFromItem(item).row()
        self.join(self.data[indx])
    
    def set_games(self, games):
        self.clear()
        for game in games:
            item = QtGui.QListWidgetItem(game['name'])
            self.gamelist.addItem(item)
            self.data.append(game['uid'])


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
        
        for widg in (self.server, self.user, self.passwd):
            self.connect(widg, 
                         QtCore.SIGNAL('returnPressed()'),
                         self,
                         QtCore.SLOT('accept()'))
        
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
        main.addLayout(but)
        main.addStretch(1)
        self.setLayout(main)


class ServerWindow(QtGui.QMainWindow):
    def __init__(self, host=None, port=None, login_user=None, login_pwd=None,
                 conn=None):
        QtGui.QMainWindow.__init__(self)
        
        self.setWindowTitle("Python Pentago - %s:%s" % (str(host), str(port)))
        
        self.gamelist = GameList(None)
        self.setCentralWidget(self.gamelist)
        
        self.login_user = login_user
        self.login_pwd = login_pwd
        
        self.connection = None
        self.attempts = 5
        
        self.player_cls = LocalPlayer
        
        disconnect = QtGui.QAction('&Disconnect', self)
        disconnect.setShortcut('Ctrl+Q')
        disconnect.setStatusTip('Disconnect from server')
        self.connect(disconnect, QtCore.SIGNAL('triggered()'),
                     self.disconnect)
        
        new_game = QtGui.QAction('&New Game', self)
        new_game.setShortcut('Ctrl+N')
        new_game.setStatusTip('Open a new game')
        self.connect(new_game, QtCore.SIGNAL('triggered()'),
                     self.new_game)
        
        join_game = QtGui.QAction('&Join Game', self)
        join_game.setShortcut('Ctrl+J')
        join_game.setStatusTip('Join a game.')
        self.connect(join_game, QtCore.SIGNAL('triggered()'),
                     self.join_game)
        
        settings = QtGui.QAction('&Settings', self)
        settings.setStatusTip('Adjust settings')
        self.connect(new_game, QtCore.SIGNAL('triggered()'),
                     self.settings)
        
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(new_game)
        file_menu.addAction(join_game)
        file_menu.addSeparator()
        file_menu.addAction(disconnect)
        
        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(settings)
        
        self.need_connected = [disconnect, new_game, join_game, self.gamelist]
        for widg in self.need_connected:
            widg.setEnabled(False)
        
        if conn is not None:
            self.connection = conn
        elif host and port:
            self.init_conn(host, port)
    
    def init_conn(self, host, port):
        ClientConnection.start_new(host, port, self, self.connected)
    
    @classmethod
    def from_string(cls, string, login_user=None, login_pwd=None):
        host, port = parse_ip(string, DEFAULT_PORT)
        return cls(host, port, login_user, login_pwd)
    
    def connected(self, conn):
        if self.login_user and self.login_pwd:
            conn.authenticate(self.login_user, self.login_pwd)
        self.connection = conn
        self.statusBar().showMessage("Connection to server established", 10000)
        for widg in self.need_connected:
            widg.setEnabled(True)
        self.gamelist.join = conn.join_game
    
    def disconnect(self):
        self.close()
    
    def new_game(self):
        name, ok = (
            QtGui.QInputDialog.getText(self, "Enter game name", "Game name:")
        )
        if ok:
            self.connection.new_game(str(name))
    
    def settings(self):
        pass
    
    def join_game(self):
        name, ok = (
            QtGui.QInputDialog.getInteger(self, "Enter game id", "Game id:")
        )
        if ok:
            self.connection.join_game(int(name))
    
    def show_game(self, game):
        g = GameWindow(game)
        g.show()
    
    def show_games(self, games):
        self.gamelist.set_games(games)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    s = ServerWindow(0, 0)
    s.show()
    app.exec_()
