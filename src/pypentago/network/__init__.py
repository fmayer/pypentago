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

""" This module contains the Connection class which can be used by server and 
client without modifications. It should be passed to server.startServer or to
client.run_client as the prot attribute """

import sys
import inspect

from collections import defaultdict

if sys.version_info[:2] > (2, 5):
    # In Python 2.6+, use built-in JSON support.
    from json import dumps, loads
else:
    # Pre Python 2.6 we need simplejson installed.
    from simplejson import dumps, loads

from twisted.protocols.basic import LineOnlyReceiver


def getmembers(object, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    # I am aware that this is already implemented in inspect, but
    # a) It's better when it's a generator
    # b) I need it to swallow exceptions, some frameworks raise them
    #    when getting attributes. Don't ask me...
    for key in dir(object):
        try:
            value = getattr(object, key)
        except Exception:
            # Yes. That happens! I'm looking at you, wxPython!
            # We shouldn't need these members anyway. Go on.
            continue
        if not predicate or predicate(value):
            yield (key, value)


def expose(*actions):
    def decorate(exc):
        if not actions:
            exc._bind_to.append(exc.__name__)
        else:
            if not hasattr(exc, '_bind_to'):
                exc._bind_to = []
            exc._bind_to.extend(actions)
        return exc
    return decorate


def require_auth(f):
    f.auth = True
    return f


class BadInput(Exception):
    pass


class Connection(LineOnlyReceiver):
    delimiter = "\0"
    encoding = "utf-8"
    """ The Connection class. Please do not overwrite anything unless you 
    really know what you are doing or otherwise stated """
    
    def construct(self):
        """ This is called when the Connection
        instance's __init__ is called """
    
    def init(self):
        """ This method is called once connection is established. Feel free to 
        overwrite it to your needs """
    
    def destruct(self, reason):
        """ This method is called once the connection is lost. Feel free to 
        overwrite it """
    
    def internal_error(self, request):
        """ This is called when a handler raises an exception.
        Get the information about the exception using sys.exc_info(). """
    
    def bad_input(self, request):
        """ This is called when a handler raises BadInput.
        Get the information about the exception using sys.exc_info(). """
    
    def malformed_request(self, request):
        """ This is called when there is an error while parsing the JSON
        received. """
    
    def no_handler(self, evt):
        """ This is called when a keyword is received that no handler is
        registered for. """
    
    def __init__(self):
        self.binds = defaultdict(list)
        self.auth = False
        self.construct()
        # This only helps pylint and IDEs, no real use at all.
        self.factory = None
        for name, method in getmembers(self):
            if hasattr(method, '_bind_to'):
                for bind_to in method._bind_to:
                    self.binds[bind_to].append(method) 
    
    def lineReceived(self, income_data):
        """ This method handles received data and forwards it to the correct 
        event handlers """
        # NOTE: All exceptions that appear unhandled in here cause the
        # connection to be closed.
        income_data = income_data.decode(self.encoding)
        if not income_data:
            return
        
        try:
            keyword, data = loads(income_data)
        except Exception:
            self.malformed_request(income_data)
            return
        event = {'keyword': keyword, 'data': data}
        
        funs = self.binds[keyword]
        
        if not self.auth and any(getattr(h, 'auth', False) for h in funs):
            self.send("AUTHREQ")
            return
        
        if funs:
            for fun in funs:
                # We swallow the exception here. The handlers are responsible
                # for reporting (e.g. logging) them.
                try:
                    self._handle_return(fun(event))
                except BadInput:
                    self._handle_return(self.bad_input(income_data))
                except Exception:
                    self._handle_return(self.internal_error(income_data))
        else:
            self._handle_return(self.no_handler(event))
    
    def bind(self, keyword, function):
        """ Bind the keyword to the function, this function has to accept one 
        attribute being the event """
        if not callable(function):
            raise TypeError("Function has to be callable")
        self.binds[keyword].append(function)
    
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
        send = dumps([keyword, data]).encode(self.encoding)
        self.sendLine(send)
    
    def _handle_return(self, ret):
        if ret is not None:
            if isinstance(ret, basestring):
                self.send(ret)
            else:
                self.send(*ret)
    
    def close(self):
        self.transport.loseConnection()
