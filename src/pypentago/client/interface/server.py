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

# from pypentago.client.connection import ClientConnection
# from pypentago import DEFAULT_PORT

DEFAULT_PORT = 29560

class ServerWindow(QtGui.QMainWindow):
    def __init__(self, host, port):
        QtGui.QMainWindow.__init__(self)
        
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
        self.init_conn()
    
    def init_conn(self):
        # DEBUG:
        self.connected(None)
        # Real Code:
        # ClientConnection.start_new(host, port, self.connected,
        #                            self.conn_failed)
    
    @classmethod
    def from_string(cls, string):
        h = string.split(':')
        if len(h) == 1:
            return cls(string, DEFAULT_PORT)
        elif len(h) == 2:
            return cls(h[0], h[1])
        else:
            raise ValueError("Cannot interpret %r as server connect string!"
                             % string)
    
    def connected(self, conn):
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
    
    def conn_failed(self, connector):
        if self.attempts >= 0:
            self.attempts -= 1
            # Retry
            connector.connect()
        else:
            # Inform user connection cannot be established and die.
            pass        


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    s = ServerWindow(0, 0)
    s.show()
    app.exec_()
