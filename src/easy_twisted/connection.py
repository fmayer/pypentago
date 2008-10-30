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

""" This module contains the Connection class which can be used by server and 
client without modifications. It should be passed to server.startServer or to
client.run_client as the prot attribute """

import sys

import actions

if sys.version_info[:2] > (2, 5):
    # In Python 2.6+, use built-in JSON support.
    from json import dumps, loads
else:
    # Pre Python 2.6 we need simplejson installed.
    from simplejson import dumps, loads

from twisted.protocols.basic import LineOnlyReceiver

from easy_twisted.evt import Event, BIND_ANY


expose = actions.register_method


class Connection(actions.ActionHandler, LineOnlyReceiver):
    delimiter = "\3"
    """ The Connection class. Please do not overwrite anything unless you 
    really know what you are doing or otherwise stated """
    
    def construct(self):
        pass
    
    def init(self):
        """ This method is called once connection is established. Feel free to 
        overwrite it to your needs """
        pass
    
    def destruct(self):
        """ This method is called once the connection is lost. Feel free to 
        overwrite it """
        pass
    
    def __init__(self):
        self.binds = {}
        self.debug = False
        self.construct()

    def lineReceived(self, income_data):
        """ This method handles received data and forwards it to the correct 
        event handlers """
        income_data = income_data.decode('utf-8')
        if income_data:
            keyword, data = loads(income_data)
            event = Event(self, keyword, data)
            ret = event.raise_event()
    
    def onAny(self, evt):
        """ This method is called if BIND_ANY is not bound and an unknown 
        keyword is received """
        raise NotImplementedError("Please either use BIND_ANY or "
                                  "override onAny")
    
    def bind(self, keyword, function, *args, **kwargs):
        """ Bind the keyword to the function, this function has to accept one 
        attribute being the event """
        if not callable(function):
            raise TypeError("Function has to be callable")
        self.context.register_handler(keyword, function, *args, **kwargs)
    
    def connectionMade(self):
        """ Internal function that appends this connection to the client list 
        of the factory """
        self.factory.clients.append(self)
        self.init()
    
    def connectionLost(self, reason):
        """ Internal function deleting the connection from the client list when 
        the connection is lost """
        self.factory.clients.remove(self)
        self.destruct(reason)
    
    def send(self, keyword, data=None):
        """ Send keyword to the other side. If data is passed, it can be 
        obtained by the other side using Event.arg_list """
        send = dumps([keyword, data])
        send = send.encode('utf-8')
        self.transport.write(send + self.delimiter)
