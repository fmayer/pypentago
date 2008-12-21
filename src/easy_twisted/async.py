import asyncore, socket


def tick():
    """ Call this in your application's main loop. """
    asyncore.loop(count=1, timeout=0)


class Connection(asyncore.dispatcher):
    delimiter = "\r\n"
    buffer_size = 1024
    def __init__(self, sock=None):
        asyncore.dispatcher.__init__(self, sock)
        self.encoding = None
        self.write_buffer = ''
        self.read_buffer = ''
        self.size = None

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
    
    def _conn_lost(self):
        """ Internal cleanup actions. Do not override! """
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
    
    def fixed_length(self, size):
        """ For the next size bytes, ignore the delimiter and directly
        pass them to data_received once they've been fully received """
        self.size = size
    
    def send(self, msg):
        self.write_buffer += msg + self.delimiter

    def split_buffer(self):
        split = self.read_buffer.split(self.delimiter)
        self.read_buffer = split[-1]
        return split[:-1]

    def parse_buffer(self):
        for elem in self.split_buffer():
            if self.encoding is not None:
                read = read.decode(self.encoding)
            self.line_received(read)

    def handle_connect(self):
        self.connection_made()

    def handle_close(self):
        self._conn_lost()
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


class Client(Connection):
    def __init__(self, host, port):
        Connection.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))


class ServerHandler(Connection):
    def __init__(self, sock, remote_add, parent):
        Connection.__init__(self, sock)
        self.remote_add = remote_add
        self.parent = parent
    
    def _conn_lost(self):
        if self in self.parent.connections:
            self.parent.connections.remove(self)


class Server(asyncore.dispatcher):
    def __init__(self, address, handler, max_clients=0):
        asyncore.dispatcher.__init__(self)
        self.handler = handler
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.bind(address)
        except socket.error:
            # Prevent errors to occur because address was already in use
            # but the socket still exists.
            self.close()
            raise
        self.listen(max_clients)
        self.connections = []
    
    def handle_accept(self):
        (sock, addr) = self.accept()
        self.connections.append(self.handler(sock, addr, self))
    
    def serve_forever(self):
        asyncore.loop()
