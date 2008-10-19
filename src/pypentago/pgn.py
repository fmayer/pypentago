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

""" Convert a move to a PGN string or convert a PGN string to a move list """

from __future__ import with_statement

from pypentago.parser import Parser, State


class InvalidPGN(Exception):
    """ This exception is raised when a PGN passed to from_pgn
    is not valid. This means that it is either too long, too
    short or contains characters it may not 
    """
    pass


def to_pgn(field, row, column, rot_dir, rot_field):
    """ Convert field, row, column, rot_dir, rot_field to a PGN string """
    field = chr(ord("A")+int(field))
    row = chr(ord("a")+int(row))
    col = int(column)+1
    rot_dir = rot_dir
    rot_field = chr(ord("A")+int(rot_field))
    return "".join([str(a) for a in (field, row, col, rot_dir, rot_field)])


def from_pgn(pgn_string):
    """ Convert a PGN string to (field, row, column, rot_dir, rot_field). 
    
    Raises InvalidPGN if supplied with an invalid PGN string. This could be a 
    string that is too short, too long, or has characters in it that do not 
    represent a location on the board. """
    try:
        field, row, col, rot_dir, rot_field = pgn_string
    except ValueError:
        raise InvalidPGN(pgn_string)
    
    field = ord(field) -  ord("A")
    row = ord(row) - ord("a")
    col = int(col)- 1
    rot_dir = rot_dir
    rot_field = ord(rot_field) - ord("A")
    if not (field < 4 and row < 3 and col < 3 and rot_dir in ("R", "L") 
            and rot_field < 4):
        raise InvalidPGN
    return (field, row, col, rot_dir, rot_field)


def get_game_pgn(turns):
    lines = []
    max_elem = len(turns)-1
    lock = False
    for i, turn in enumerate(turns):
        if not lock:
            if i != max_elem:
                lines.append("%s\t%s" % (to_pgn(*turn), to_pgn(*turns[i+1])))
                lock = True
            else:
                lines.append(to_pgn(*turn))
        else:
            lock = False
    return "\n".join(lines)


def write_file(turns, file_name):
    """ Write the turns to file_name in PGN replay file format """
    lines = get_game_pgn(turns)
    with open(file_name, "w") as file_obj: 
        file_obj.write(lines)
                                         

class PentagoParser(Parser):
    def __init__(self):
        Parser.__init__(self)
        
        self.text = State(self)
        self.metadata = State(self, "@")
        self.comment = State(self, "#", until_eol=True)
        self.multiline_mdata = State(self, "%", True, "%")
        
        self.state = self.default_state


def parse_file(file_name):
    """ Return a list containing the turns described in a PNG file in the format
    (playerID, (field, row, col, rot_dir, rot_field)). The PNG file contains the
    seperate turns seperated by tabulators for the two turns done in a row by 
    the two players and a newline to seperate a new turn, meaning that its 
    player1's turn.
    
    # P1      P2
    Aa1LA    Aa1RA
    Ba1RC    Db2RB
    .....    ....."""
    parser = PentagoParser()
    parser.parse_file(file_name)
    pgn_strings = []
    for line in parser.text.result:
        split = line.split("\t")
        if split[0] == line:
            split = line.split(" ")
            split = [elem for elem in split if elem]
        pgn_strings.extend(split)
    
    metadata = {}
    for line in parser.metadata.result:
        key, value = line.split(" ", 1)
        metadata[key] = value

    return [from_pgn(elem) for elem in pgn_strings if len(elem) == 5]
