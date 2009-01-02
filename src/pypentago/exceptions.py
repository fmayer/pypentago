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
