# pyPentago - a board game
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

__version__ = "svn"
__authors__ = [ "Florian Mayer <flormayer@aim.com>", "J. Kovacs", 
                "Abishek Goda", "Hardik Metha", 
                u'Mathias "DarkKiller" K\xe6rlev']
__artists__ = ["Kenichi \"XenoSilence\" Lei", ]
__url__ = "https://gna.org/projects/pypentago/"
__copyright__ = "(c) 2008 Florian Mayer"
__license__ = "GNU General Public License version 3"
__description__ = ("pyPentago is an open source effort "
                   "to recreate the boardgame Pentago.\n"
                   "It has a fully implemented "
                   "multiplayer modus.")
__bugs__ = "https://gna.org/bugs/?func=additem&group=pypentago"


PROTOCOL_VERSION = 1
EMAIL_REGEX = r"""^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$"""

# Map arguments to logging verbosity levels:
verbosity_levels = {
    -1: 40, # -q
    0: 30,  # default
    1: 20,  # -v
    2: 10,  # -vv
}

from os.path import dirname, join

script_path = dirname(__file__)
IMGPATH = join(script_path, "client", "img")

# -----------------------------------------------------------------------------
# BASIC FUNCTIONS NEEDED IN MANY MODULES FOLLOW
# -----------------------------------------------------------------------------

def could_int(string):
    """ could_int(string) -> bool
    
    Check if a string can be converted to an int or not """
    try:
        int(string)
        return True
    except ValueError:
        return False

def get_rand_str(min_length=13, max_length=18):
    """ get_rand_str(min_length=13, max_length=18) -> str 
    
    Get a random string with minimum length of min_length and maximum length 
    of max_length """
    from string import ascii_letters
    from random import randint, choice
    # Variable lenght of random string for improved security:
    lenght = randint(min_length, max_length)
    rand = [choice(ascii_letters) for elem in range(lenght)]
    rand_str = "".join(rand)
    return rand_str

def int_all(lst):
    """ int_all(sequence) -> sequence
    
    Convert all objects in lst that can be converted to an int to an int
    and leave the others as they are """
    ret = []
    for elem in lst:
        if could_int(elem):
            ret.append(int(elem))
        else:
            ret.append(elem)
    return ret
