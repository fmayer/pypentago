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

""" This is the main pypentago module containing basic constants about 
pypentago such as version, protocol version or the regex the email 
addresses have to match. """

import os
import sys
import time
import logging
import __builtin__
import logging.handlers

from string import ascii_letters
from random import randint, choice
from traceback import format_exception

__version__ = "devel"
__authors__ = [ "Florian Mayer <flormayer@aim.com>", 
                u'Mathias "DarkKiller" K\xe6rlev']
__artists__ = ["Kenichi \"XenoSilence\" Lei", ]
__url__ = "http://bitbucket.org/segfaulthunter/pypentago/"
__copyright__ = "(c) 2008 Florian Mayer"
__license__ = "GNU General Public License version 3"
__description__ = ("pypentago is an open source effort "
                   "to recreate the boardgame Pentago.\n"
                   "It has a fully implemented "
                   "multiplayer modus.")
__bugs__ = "http://bitbucket.org/segfaulthunter/pypentago/issues/"


PROTOCOL_VERSION = 1
EMAIL_REGEX = r"""^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$"""
DEFAULT_PORT = 26500

# Dummy gettext.
__builtin__._ = lambda x: x

class _CW:
    """ Equals "CW" and "R" """
    def __eq__(self, other):
        return self is other or other == "CW" or other == "R"
    
    def __neq__(self, other):
        return not self == other
    
    @staticmethod
    def __str__():
        # PGN needs that until it is changed.
        return "R"


class _CCW:
    """ Equals "CCW" and "L" """
    def __eq__(self, other):
        return self is other or other == "CCW" or other == "L"
    
    def __neq__(self, other):
        return not self == other
    
    @staticmethod
    def __str__():
        # PGN needs that until it is changed.
        return "L"


# Singleton representing clockwise rotation
CW = _CW()
# Singleton representing counter-clockwise rotation
CCW  = _CCW()


def get_rotation(string):
    if string == CW:
        return CW
    elif string == CCW:
        return CCW
    else:
        raise ValueError


# Map arguments to logging verbosity levels:
verbosity_levels = {
    -1: 40, # -q
    0: 30,  # default
    1: 20,  # -v
    2: 10,  # -vv
}

data = {}

script_path = os.path.dirname(__file__)
IMGPATH = os.path.join(script_path, 'data')

for file_ in os.listdir(IMGPATH):
    data[file_] = os.path.abspath(os.path.join(IMGPATH, file_))


def log_exception(err):
    log = logging.getLogger("pypentago.exception")
    log.critical("Caught exception:\n"+''.join(format_exception(*err)))


def except_hook(exctype, value, tceback):
    log_exception((exctype, value, tceback))


def init_logging(log_file, cnsl_verbosity):
    file_formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    # Use UTC for files.
    file_formatter.converter = time.gmtime
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(0)
    
    cnsl_formatter = logging.Formatter(
        '%(name)-12s: %(levelname)-8s %(message)s'
    )
    # Use local time for output.
    cnsl_formatter.converter = time.localtime
    
    cnsl_handler = logging.StreamHandler()
    cnsl_handler.setFormatter(cnsl_formatter)
    cnsl_handler.setLevel(cnsl_verbosity)
    
    # add the handler to the root logger
    logging.getLogger().addHandler(cnsl_handler)
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(0)
    
    sys.excepthook = except_hook
