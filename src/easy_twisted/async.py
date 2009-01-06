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


import asyncore
import socket
import select


if hasattr(select, 'poll'):
    poll = asyncore.poll2
else:
    poll = asyncore.poll
poll.__doc__ = ("Poll the connection's sockets for changes. "
                "Run this in your mainloop")


class Connection(asyncore.dispatcher):
    delimiter = "\r\n"
    buffer_size = 1024
    def __init__(self, sock=None, conn_lost=None):
        asyncore.dispatcher.__init__(self, sock)
        self.encoding = None
        self.write_buffer = ''
        self.read_buffer = ''
        self.size = None
        # If used as a client, those will stay None.
        self.remote_addr = None
        self.factory = self.server = None
        self._conn_lost = conn_lost
    
    @classmethod
    def as_server_handler(cls, sock, remote_addr, server):
        inst = cls(sock, lambda x: server.clients.remove(x))
        inst.remote_addr = remote_addr
        inst.factory = inst.server = server
        return inst
    
    @classmethod
    def as_client(cls, host, port):
        inst = cls()
        inst.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        inst.connect((host, port))
        return inst
    
    def data_received(self, data):
        """ [Override] """
        pass
    
    def line_received(self, line):
        """ [Override] """
        pass
    
    def connection_made(self):
        """ [Override] """
        pass
    
    def connection_lost(self):
        """ [Override] """
        pass
    
    def _data_recv(self):
        """ Internal. Do not override! """
        if self.size is not None and len(self.read_buffer) >= self.size:
            # We fully received the fixed-length data.
            read = self.read_buffer[:self.size]
            # There may be more than the data we wanted, store rest in
            # read buffer.
            self.read_buffer = self.read_buffer[self.size:]
            self.data_received(read)
            # Future data will be received normally with the delimiter.
            # Any remaining data in the read buffer will be parsed by
            # handle_read, because it checks for self.size after running
            # _data_recv.
            self.size = None
    
    def receive_data(self, size):
        """ For the next size bytes, ignore the delimiter and directly
        pass them to data_received once they've been fully received """
        self.size = size
    
    def send_line(self, msg):
        self.write_buffer += msg + self.delimiter
    
    def split_buffer(self):
        split = self.read_buffer.split(self.delimiter)
        self.read_buffer = split.pop()
        return split
    
    def parse_buffer(self):
        for read in self.split_buffer():
            if self.encoding is not None:
                read = read.decode(self.encoding)
            self.line_received(read)
    
    def handle_connect(self):
        self.connection_made()
    
    def handle_close(self):
        if self._conn_lost is not None:
            self._conn_lost(self)
        self.connection_lost()
        self.close()
    
    def handle_read(self):
        self.read_buffer += self.recv(self.buffer_size)
        self._data_recv()
        if self.size is not None:
            # We're receiving fixed-length data. Ignore delimiter.
            return
        self.parse_buffer()
    
    def handle_write(self):
        sent = asyncore.dispatcher.send(self, self.write_buffer)
        self.write_buffer = self.write_buffer[sent:]
    
    def writable(self):
        # If there's something in the buffer, we want to write it.
        return self.write_buffer
    
    def readable(self):
        # We're open to read anytime.
        return True
    
    # Twisted LineOnlyReceiver API compatibility.
    connectionMade = connection_made
    connectionLost = connection_lost
    lineReceived = line_received
    sendLine = send_line


class Server(asyncore.dispatcher):
    def __init__(self, address=None, handler=None):
        asyncore.dispatcher.__init__(self)
        self.handler = handler
        if address is not None:
            self.bind(address)
        self.connections = []
    
    def bind(self, address):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.bind(address)
        except socket.error:
            # Prevent errors to occur because address was already in use
            # but the socket still exists.
            self.close()
            raise
    
    def handle_accept(self):
        (sock, addr) = self.accept()
        self.connections.append(
            self.handler.as_server_handler(sock, addr, self)
        )
    
    def serve_forever(self, max_clients):
        self.listen(max_clients)
        asyncore.loop(None, True)
