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

""" This module contains *ALL* costum exceptions that may be raised in 
pypentago """


class InvalidTurn(Exception):
    """ Raised when something is wrong with the passed turn. 
    Most likely it contains a position that's not on the board. """
    pass


class SquareNotEmpty(Exception):
    """ Raised when attempting to set to a position where there already is a 
    gaming-piece. """
    pass


class NotYourTurn(Exception):
    """ Raised when attemption to set a stone although it's not your turn """
    pass


class GameFull(Exception):
    """ Raised when trying to join a game that is already full """
    pass


class NoSuchRoom(Exception):
    """ Raised when a room doesn't exist. """
    pass


class InvalidPGN(Exception):
    """ PGN string malformed. """
    pass


class NotInDB(Exception):
    """ Searched item doesn't exist in the database. """
    pass


class InvalidPlayerID(Exception):
    pass


class NoDB(Exception):
    """ Doing an action that needs you to be connected to a database, 
    but we are not. """
    pass
