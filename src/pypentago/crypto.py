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


import string
import random
import hashlib


SALT_POOL = string.ascii_letters + string.digits


class Plain:
    def __init__(self):
        self.s = ''
    
    def update(self, s):
        self.s += s
    
    def hexdigest(self):
        return self.s


methods = {
    'sha': hashlib.sha1,
    'sha256': hashlib.sha256,
    'sha512': hashlib.sha512,
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'plain': Plain
}


def _gen_from_pool(len_, pool):
    return ''.join(random.choice(pool) for _ in xrange(len_))


def gen_salt(len_):
    return _gen_from_pool(len_, SALT_POOL)


def hash_pwd(pwd, method='sha'):
    if method.lower() in methods:
        h = methods[method.lower()]()
    else:
        raise ValueError("Unknown method")
    salt = gen_salt(6)
    h.update(salt)
    h.update(pwd)
    return "%s$%s$%s" % (method, salt, h.hexdigest())


def check_pwd(pwd, pwhash):
    method, salt, hash_ = pwhash.split("$")
    if method.lower() in methods:
        h = methods[method.lower()]()
    else:
        raise ValueError("Unknown method")
    h.update(salt)
    h.update(pwd)
    return hash_ == h.hexdigest()
