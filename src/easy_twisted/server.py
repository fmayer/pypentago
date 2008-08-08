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

""" This module contains the function that is necessary to start a server """

from twisted.internet import reactor, protocol
from connection import Connection
def startServer(port, prot=None, factory=None):
    """ Run server on port. Either prot or factory has to be passed. If only 
    prot is passed, a default factory will be made. If factory is passed but 
    it does not contain a protocol, prot has to be passed as well.
    
    The factory can be used to exchange data between the clients trough its 
    attributes. """
    if not (prot or factory):
        raise AttributeError("Either specify the protocol or the factory "
              "containing the protocol")
    if not factory:
        factory = protocol.ServerFactory()
        factory.clients = []
    if not factory.protocol:
        if prot:
            factory.protocol = prot
        else:
            raise AttributeError("No protocol passed and factory does not "
                  "have a protocol attribute")
    reactor.listenTCP(port,factory)
    reactor.run()

