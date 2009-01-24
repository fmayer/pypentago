#! /usr/bin/env python
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


# Fix the PYTHONPATH so we needn't have src in it.
import sys
from os.path import dirname, abspath, join
sys.path.append(abspath(join(dirname(__file__), "..")))
# End of prefix for executable files.

import unittest
import socket
import select
import errno
import time
try:
    import json
except ImportError:
    import simplejson as json
import multiprocessing

from pypentago.server.server import run_server
from pypentago import crypto

def free_port(min_, max_):
    for p in xrange(min_, max_):
        avail = True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', p))
        except socket.error, e:
            if e.errno == errno.EADDRINUSE:
                avail = False
            else:
                raise
        if avail:
            return p

PORT = free_port(20000, 65000)

class ServerTest(unittest.TestCase):
    def setUp(self):
        self.p = multiprocessing.Process(target=run_server, args=(PORT, ))
        self.p.start()
        # Give the server some time to get up.
        time.sleep(0.05)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = False
        start = time.time()
        while not conn:
            if time.time() > start + 5:
                # This is taking way too long!
                raise OSError("Couldn't connect to server")
            try:
                self.client.connect(('', PORT))
                conn = True
            except socket.error, e:
                if e.errno == errno.ECONNREFUSED:
                    time.sleep(0.1)
                else:
                    raise
    
    def tearDown(self):
        self.p.terminate()
    
    def test_nauth(self):
        self.client.send(json.dumps(['OPEN', 'foo']) + '\0')
        recv = self.client.recv(100)
        recvs = recv.split('\0')
        self.assertEquals(recvs[1], '')
        keyword, data = json.loads(recvs[0])
        self.assertEquals(keyword, "AUTHREQ")
    
    def test_register(self):
        send = ["REGISTER", {'login': 'hitch', 'passwd': 'trillian',
                             'real_name': 'Arthur Dent', 
                             'email': 'arthur@dent.co.uk'}]
        self.client.send(json.dumps(send) + '\0')
        recv = self.client.recv(100)
        recvs = recv.split('\0')
        keyword, data = json.loads(recvs[0])
        self.assertEqual(keyword, "REGISTERED")
    
    def test_multiple_login(self):
        send = ["REGISTER", {'login': 'hitch', 'passwd': 'trillian',
                             'real_name': 'Arthur Dent', 
                             'email': 'arthur@dent.co.uk'}]
        self.client.send(json.dumps(send) + '\0')
        recv = self.client.recv(100)
        self.client.send(json.dumps(send) + '\0')
        recv = self.client.recv(100)
        recvs = recv.split('\0')
        keyword, data = json.loads(recvs[0])
        self.assertEqual(keyword, "REGFAILED")
    
    def test_login(self):
        self.test_register()
        self.client.send(json.dumps(["LOGIN", {'login': "hitch", 
                                               'passwd': 'trillian'}]) + '\0')
        recv = self.client.recv(100)
        recvs = recv.split('\0')
        keyword, data = json.loads(recvs[0])
        self.assertEqual(keyword, "AUTH")
    
    def test_auth(self):
        self.test_login()
        self.client.send(json.dumps(['OPEN', 'foo']) + '\0')
        recv = self.client.recv(100)
        recvs = recv.split('\0')
        self.assertEquals(recvs[1], '')
        keyword, data = json.loads(recvs[0])
        self.assertEquals(keyword, "OPENGAME")
        return data
    
    def test_join(self):
        opened_game = self.test_auth()
        other_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        other_client.connect(('', PORT))
        send = ["REGISTER", {'login': 'glados', 'passwd': 'triumph',
                             'real_name': 'Aperture Science', 
                             'email': 'glades@aperturescience.com'}]
        other_client.send(json.dumps(send) + '\0')
        recv = other_client.recv(100)
        recvs = recv.split('\0')
        keyword, data = json.loads(recvs[0])
        self.assertEqual(keyword, "REGISTERED")
        other_client.send(json.dumps(["LOGIN", {'login': "glados", 
                                               'passwd': 'triumph'}]) + '\0')
        recv = other_client.recv(100)        
        other_client.send(json.dumps(["JOIN", opened_game]) + '\0')
        recv = other_client.recv(100)
        recvs = recv.split('\0')
        keyword, data = json.loads(recvs[0])
        self.assertEqual(keyword, "INITGAME")
        o_recv = self.client.recv(100)
        o_recvs = o_recv.split('\0')
        keyword, data = json.loads(o_recvs[0])
        self.assertEqual(keyword, "INITGAME")
        rest = recvs[1] or o_recvs[1]
        r, w, e = select.select([self.client, other_client], [], [], 0)
        if r:
            rest += r[0].recv(100)
        keyword, data = json.loads(rest)
        self.assertEqual(keyword, "GAME")
        self.assertEqual(data, [opened_game, 'LOCALTURN'])
        return opened_game, other_client, recvs[1]
    
    def test_turn(self):
        turn = [0, 0, 0, 'L', 0]
        uid, other_client, is_turn = self.test_join()
        a = is_turn and other_client or self.client
        b = is_turn and self.client or other_client
        a.send(json.dumps(['GAME', [uid, 'TURN', turn]]) + '\0')
        # print a.recv(100)
        recv = b.recv(100)
        recvs = recv.split('\0')
        keyword, data = json.loads(recvs[0])
        self.assertEqual(keyword, "GAME")
        self.assertEqual(data, [uid, "TURN", turn])
        return a
        

if __name__ == "__main__":
    unittest.main()
