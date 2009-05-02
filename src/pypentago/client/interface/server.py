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

import sys
import os

from ConfigParser import ConfigParser

from PyQt4 import QtGui, QtCore

import pypentago
from pypentago import util, conf

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
                 conn=None, title=None):
        QtGui.QMainWindow.__init__(self)
        
        if not title:
            title = "%s:%s" % (str(host), str(port))
        
        self.setWindowTitle("Python Pentago - %s" % title)
        self.setWindowIcon(
            QtGui.QIcon(pypentago.data['icon.png'])
        )
        
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
        
        settings = QtGui.QAction('&Settings', self)
        settings.setStatusTip('Adjust settings')
        self.connect(new_game, QtCore.SIGNAL('triggered()'),
                     self.settings)
        
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(new_game)
        file_menu.addSeparator()
        file_menu.addAction(disconnect)
        
        edit_menu = menubar.addMenu('&Edit')
        edit_menu.addAction(settings)
        
        self.need_connected = [disconnect, new_game, self.gamelist]
        self.need_disconnected = []
        
        for widg in self.need_connected:
            widg.setEnabled(False)
        for widg in self.need_disconnected:
            widg.setEnabled(True)
        
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
    
    @classmethod
    def from_serverinfo(cls, serverinfo):
        host, port = parse_ip(serverinfo.address, DEFAULT_PORT)
        return cls(host, port, serverinfo.user, serverinfo.password,
                   title=serverinfo.name)
    
    def connected(self, conn):
        if self.login_user and self.login_pwd:
            conn.authenticate(self.login_user, self.login_pwd)
        self.connection = conn
        self.statusBar().showMessage("Connection to server established")
        for widg in self.need_connected:
            widg.setEnabled(True)
        for widg in self.need_disconnected:
            widg.setEnabled(False)
        self.gamelist.join = conn.join_game
    
    def connection_lost(self, reason):
        self.statusBar().showMessage(
            "Connection to server lost - %s" % reason.getErrorMessage()
        )
        for widg in self.need_connected:
            widg.setEnabled(False)
        for widg in self.need_disconnected:
            widg.setEnabled(True)
    
    def disconnect(self):
        self.close()
    
    def new_game(self):
        name, ok = (
            QtGui.QInputDialog.getText(self, "Enter game name", "Game name:")
        )
        if ok:
            self.connection.new_game(unicode(name))
    
    def settings(self):
        pass
    
    def show_game(self, game):
        g = GameWindow(game)
        g.show()
    
    def show_games(self, games):
        self.gamelist.set_games(games)


class ServerBrowser(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        
        self.serverinfos = []
        
        layout = QtGui.QVBoxLayout()
        inputlayout = QtGui.QGridLayout()
        buttonlayout = QtGui.QHBoxLayout()
        
        self.name = QtGui.QLineEdit(self)
        self.address = QtGui.QLineEdit(self)
        self.user = QtGui.QLineEdit(self)
        self.password = QtGui.QLineEdit(self)
        self.description = QtGui.QLineEdit(self)
        
        self.serverlist = QtGui.QTreeWidget()
        self.serverlist.setHeaderLabels(['Name', 'Address', 'Login', 'Description'])
        
        self.reset = QtGui.QPushButton('Reset')
        self.add = QtGui.QPushButton('Add')
        self.remove = QtGui.QPushButton('Remove')
        self.connect_ = QtGui.QPushButton('Connect')
        
        inputlayout.addWidget(QtGui.QLabel('Name: '), 0, 0)
        inputlayout.addWidget(self.name, 0, 1)
        inputlayout.addWidget(QtGui.QLabel('Address: '), 0, 2)
        inputlayout.addWidget(self.address, 0, 3)
        inputlayout.addWidget(QtGui.QLabel('User: '), 1, 0)
        inputlayout.addWidget(self.user, 1, 1)
        inputlayout.addWidget(QtGui.QLabel('Password: '), 1, 2)
        inputlayout.addWidget(self.password, 1, 3)
        inputlayout.addWidget(QtGui.QLabel('Description: '), 2, 0)
        inputlayout.addWidget(self.description, 2, 1, 1, 3)
        
        buttonlayout.addWidget(self.reset)
        buttonlayout.addWidget(self.add)
        buttonlayout.addWidget(self.remove)
        buttonlayout.addWidget(self.connect_)
        
        layout.addLayout(inputlayout, 0)
        layout.addWidget(self.serverlist, 1)
        layout.addLayout(buttonlayout, 0)
        
        self.setLayout(layout)
        
        QtCore.QObject.connect(
            self.reset, QtCore.SIGNAL('clicked()'), self.reset_clicked
        )
        QtCore.QObject.connect(
            self.add, QtCore.SIGNAL('clicked()'), self.add_clicked
        )
        QtCore.QObject.connect(
            self.remove, QtCore.SIGNAL('clicked()'), self.remove_clicked
        )
        QtCore.QObject.connect(
            self.connect_, QtCore.SIGNAL('clicked()'), self.connect_clicked
        )
        
        QtCore.QObject.connect(
            self.serverlist,
            QtCore.SIGNAL("itemDoubleClicked ( QTreeWidgetItem * , int  )"),
            self.itemdouble
        )
        QtCore.QObject.connect(
            self.serverlist,
            QtCore.SIGNAL("itemActivated ( QTreeWidgetItem * , int  )"),
            self.itemsingle
        )
    
    def set_servers(self, servers):
        self.serverlist.clear()
        for server in servers:
            item = QtGui.QTreeWidgetItem(
                [server.name or server.address, server.address,
                 server.user or '', server.description or '']
            )
            self.serverlist.addTopLevelItem(item)
        
        self.serverinfos = servers
    
    def reset_clicked(self):
        for widget in [self.name, self.address, self.user, self.password,
                       self.description]:
            widget.setText('')
    
    def add_clicked(self):
        info = self.server_info()
        if not info.address and not info.identifier:
            return
        self.serverinfos.append(info)
        self.set_servers(self.serverinfos)
        
        self.dump_config()
        
    def remove_clicked(self):
        items = self.serverlist.selectedItems()
        for item in items:
            indx = self.serverlist.indexFromItem(item).row()
            self.serverinfos.pop(indx)
            self.serverlist.takeTopLevelItem(indx)
        
        self.dump_config()
    
    def connect_clicked(self):
        server = self.server_info()
        window = ServerWindow.from_serverinfo(server)
        window.show()
    
    def itemdouble(self, item, col):
        indx = self.serverlist.indexFromItem(item).row()
        server = self.serverinfos[indx]
        window = ServerWindow.from_serverinfo(server)
        window.show()
    
    def itemsingle(self, item, col):
        indx = self.serverlist.indexFromItem(item).row()
        server = self.serverinfos[indx]
        
        self.name.setText(server.name or '')
        self.address.setText(server.address or '')
        self.user.setText(server.user or '')
        self.password.setText(server.password or '')
        self.description.setText(server.description or '')
    
    def server_info(self):
        return util.ServerInfo(
            *map(str, [self.address.text(), self.name.text(),
                       self.description.text(),
                       self.user.text(), self.password.text()]
                 )
        )
    
    def dump_config(self):
        ids = []
        
        config = conf.possible_configs('client.ini').next()
        parser = ConfigParser()
        parser.read(config)
        
        for section in parser.sections():
            if section not in ['client', 'servers']:
                parser.remove_section(section)
        
        for server in self.serverinfos:
            ids.append(server.dump(parser))
        
        with open(config, 'w') as fp:
            parser.write(fp)


if __name__ == '__main__':
    config = ConfigParser()
    config.read(conf.possible_configs('client.ini'))
        
    servers = conf.parse_servers(config)
    
    app = QtGui.QApplication(sys.argv)
    s = ServerBrowser()
    s.set_servers(servers.values())
    s.show()
    app.exec_()
