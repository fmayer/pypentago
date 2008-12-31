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


"""
Work with salted passwords.

A new salted password can be generated using the hash_pwd function.
It returns a string containing the hash algorithm, the salt, and the 
hash value of the salted password. The hash value is calculated by
hash(salt + pwd).

>>> p = hash_pwd('foobar') # doctest: +SKIP
'sha$8sufVx$b6576070134f90fc8363162446a3255043f907d3'

It is also possible to specify the desired method to use for hashing.
Doing what is shown in the example below is not advised as it will
store the password in plain-text.

>>> p = hash_pwd('foobar', 'plain') # doctest: +SKIP
'plain$yNwkvc$yNwkvcfoobar

This example also illustrates how it works under the hood. It unites the
salt, 'yNwkvc' in this example, and the password, 'foobar', and then
applies the hash function to it, not changing it in our example.

The password hash can be checked against input using the check_pwd function.

>>> check_pwd('sha$8sufVx$b6576070134f90fc8363162446a3255043f907d3',
...           'foobar')
True
>>> check_pwd('sha$8sufVx$b6576070134f90fc8363162446a3255043f907d3',
...           'spam')
False

SALT_POOL can be adjusted in order to manipulate which characters will be
used in the salt. By default, all ASCII letters and the digits are used.
"""


import string
import random
import hashlib


SALT_POOL = string.ascii_letters + string.digits


class _Plain:
    """ Dummy object imitating the hash objects to store salted passwords
    in plain-text. It is not advised to use this! """
    def __init__(self):
        self.s = ''
    
    def update(self, s):
        """ Dummy method to simulate behaviour of hash objects. """
        self.s += s
    
    def hexdigest(self):
        """ Dummy method to simulate behaviour of hash objects. """
        return self.s


methods = {
    'sha': hashlib.sha1,
    'sha256': hashlib.sha256,
    'sha512': hashlib.sha512,
    'md5': hashlib.md5,
    'sha1': hashlib.sha1,
    'plain': _Plain
}


def hash_func(method):
    """ Return object for hashing method or raise ValueError if unknown. """
    if method.lower() in methods:
        h = methods[method.lower()]()
    else:
        raise ValueError("Unknown method")
    return h


def _gen_from_pool(len_, pool):
    """ Helper function that takes len_ random elements from pool(it doesn't
    remove them from pool), and joins them together to a string. """
    return ''.join(random.choice(pool) for _ in xrange(len_))


def gen_salt(len_):
    """ Generate string for use with a salt. """
    return _gen_from_pool(len_, SALT_POOL)


def hash_pwd(pwd, method='sha', salt_len=6):
    """ Generate a new salted password with hash algorithm method. """
    h = hash_func(method)
    salt = gen_salt(salt_len)
    h.update(salt)
    h.update(pwd)
    return '$'.join((method, salt, h.hexdigest()))


def check_pwd(pwhash, pwd):
    """ Check pwhash against pwd. """
    s = pwhash.split("$")
    if len(s) != 3:
        raise ValueError('Expected "[hash method]$[salt]$[hash]" as pwhash!')
    method, salt, hash_ = s
    h = hash_func(method)
    h.update(salt)
    h.update(pwd)
    return hash_ == h.hexdigest()
