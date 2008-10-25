# easy_twisted - a framework to easily use twisted
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

""" This module contains the function that allows you to connect to a remote 
server """

from connection import Connection

def run_client(prot, host, port, parent=None):
    """ Connect to the server host:port using prot. Parent will be passed to 
    the protocol and be accessible through self.factory.parent in your 
    Connection code. Be sure to pass the Connection instance back to the 
    parent to be able to work with it. """
    from twisted.internet import reactor, protocol
    f = protocol.ClientFactory()
    f.protocol = conn
    f.clients = []
    f.parent = parent
    reactor.connectTCP(host, port, f)

def init_wx_reactor(app):
    """ This initialises the wxreactor that allows you to use Twisted and wx 
    at the same time although both are not thread safe. Please only pass the 
    class of the wx.App rather than the instance. Returns an instance of that 
    app class, you will have to call the MainLoop manually. """
    from twisted.internet import wxreactor
    wxreactor.install()
    from twisted.internet import reactor
    reactor.registerWxApp(app)
    reactor.run()
    return app
