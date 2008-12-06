#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

""" This module contains the basic Pentago field with all the operations like 
rotating, setting a stone and win detection. """


from pypentago.exceptions import SquareNotEmpty
import logging

class Field(object):
    """
    The Basic pentago field
    """
    def applyturn(self, playerID, field, row, position, rot_dir, rot_field):
        self.set_stone(playerID, field, row, position)
        if rot_dir == "R":
            self.rotright(rot_field)
        else:
            self.rotleft(rot_field)
    
    def __init__(self):
        # 0 is nothing, 1 black stone and 2 white stone
        #self.field = zeros((4, 3, 3))
        self.log = logging.getLogger("pypentago.field")
        #self.field = numpy.zeros((4, 3, 3), dtype = int)
        self.field = []
        for i in range(4):
            self.field.append([])
            for e in range(3):
                self.field[-1].append([0, 0, 0])
    
    def clean(self):
        """
        Reset the field
        """
        self.field = []
        #self.field = numpy.zeros((4, 3, 3), dtype = int)
        for i in range(4):
            self.field.append([])
            for e in range(3):
                self.field[-1].append([0, 0, 0])
    
    def rotleft(self, no):
        """
        Rotates the subboard no to the right
        """
        newfield = []
        for i in range(len(self.field[no])):
            newfield.append([])
            for k in range(3):
                newfield[i].append(self.field[no][k][i])
        newfield.reverse()
        self.field[no] = newfield
    
    def rotright(self, no):
        """
        Rotates the subboard no to the right
        """
        newfield = []
        for i in range(len(self.field[no])):
            newfield.append([])
            for k in range(3):
                newfield[i].append(self.field[no][2-k][2-i])
        newfield.reverse()
        self.field[no] = newfield

    def set_stone(self, playerID, field, row, position):
        """
        Sets a stone from the player playerID
        """
        playerID, field, row, position = (int(playerID), int(field), int(row), 
                                          int(position))
        if playerID > 2:
            raise InvalidPlayerID("Player ID %d is invalid" % playerID)
        if not self.field[field][row][position]:
            self.field[field][row][position] = playerID
            return True
        else:
            raise SquareNotEmpty(
                  "Cannot set stone at quadrant %s row %s col %s" % \
                  (field, row, position))

    def __repr__(self):
        return self.field
    
    def get_rows(self):
        rows = [self.get_row(elem) for elem in range(6)]
        return rows
    
    def get_cols(self):
        return zip(*self.get_rows())
    
    def get_col(self, col):
        return self.get_cols()[col]
    
    def __str__(self):
        string = ""
        rows = self.get_rows()
        for i, row in enumerate(rows):
            #print row
            string+="%s %s %s  %s %s %s\n" % (row[0], row[1],
                                              row[2], row[3],
                                              row[4], row[5])
            if i == 2:
                string+="\n"
            
        return string
    
    def get_row(self, rowNumber):
        if rowNumber < 3:
            fieldNumber = 0
        else:
            fieldNumber = 2
            rowNumber = rowNumber - 3
        row = list(self.field[fieldNumber][rowNumber]) + \
            list(self.field[fieldNumber+1][rowNumber])
        return row
    
    def _checkRow(self, rowNumber, playerID):
        """
        Checks both possibilities of winning in one row.
        Return 'True' when yes, else 'False'.
        """
        row = self.get_row(rowNumber)
        check = [playerID]*5
        #self.log.debug(str(row))
        if row[0:5] == check or \
           row[1:6] == check:
            return True
        else:
            return False
        
    def _checkRows(self, player):
        """
        Checks all rows for a winning 5 in a row.
        Returns 'True' if yes, else 'False'.
        """
        for row in range(6):
            if self._checkRow(row, player):
                return True
        return False

    def _checkColumn(self, columNumber, playerID):
        """
        Checks one column for both wining possibilities.
        Returns 'True' if it does, else 'False'.
        """
        check = [playerID]*5
        col = self.get_col(columNumber)
        #print col
        if list(col[0:5]) == list(check) or \
           list(col[1:6]) == list(check):
            return True
        else:
            return False

    def _checkColumns(self, player):
        """
        Checks all columns for a winning 5 in a row.
        Return 'True' if yes, else 'False'.
        """
        for columnNumber in range(6):
            if self._checkColumn(columnNumber, 
                                 player):
                return True
        return False

    def _checkDiagonalLow(self, player):
        """
        Checks the diagonals for a wining 5 in a row.
        This implementation is hardcoded, so thats not nice. :-)

        TODO:
            - Find a better solution for that!

        """
        i = player
        if (self.field[0][1][0] == i and
                self.field[0][2][1] == i and
                self.field[2][0][2] == i and
                self.field[3][1][0] == i and
                self.field[3][2][1] == i) == True:
            return True
        elif ((self.field[0][0][0] == i  and
                self.field[3][1][1] == i and
                self.field[0][1][1] == i and
                self.field[0][2][2] == i and
                self.field[3][0][0] == i)
                or (
                self.field[3][1][1] == i and
                self.field[0][1][1] == i and
                self.field[3][2][2] == i and
                self.field[0][2][2] == i and
                self.field[3][0][0] == i)):
            return True
        elif (self.field[0][0][1] == i and
                self.field[0][1][2] == i and
                self.field[1][2][0] == i and
                self.field[3][0][1] == i and
                self.field[3][1][2] == i):
            return True
        return False

    def _checkDiagonalHigh(self, player):
        """
        Checks the diagonals for a wining 5 in a row.
        This implementation is hardcoded, so thats not nice. :-)

        TODO:
            - Find a better solution for that!

        """
        i = player
        if (self.field[2][1][0] == i and
                self.field[2][0][1] == i and
                self.field[0][2][2] == i and
                self.field[1][1][0] == i and
                self.field[1][0][1] == i):
            return True
        elif ((self.field[2][2][0] == i  and
                self.field[2][1][1] == i and
                self.field[2][0][2] == i and
                self.field[1][2][0] == i and
                self.field[1][1][1] == i)
                or (
                self.field[2][1][1] == i and
                self.field[2][0][2] == i and
                self.field[1][2][0] == i and
                self.field[1][1][1] == i and
                self.field[1][0][2] == i)):
            return True
        elif (self.field[2][2][1] == i and
                self.field[2][1][2] == i and
                self.field[3][0][0] == i and
                self.field[1][2][1] == i and
                self.field[1][1][2] == i):
            return True
        return False

    def won(self):
        """
        won() -> int
        
        Wrapper for the winning condition checks.
        Returns the player instance, if a winner has been found,
        'else 'False.
        """
        for player in (1, 2):
            if self._checkRows(player):
                return player
            elif self._checkColumns(player):
                return player
            elif self._checkDiagonalHigh(player):
                return player
            elif self._checkDiagonalLow(player):
                return player
        return False
    
    cols = property(get_cols)
    rows = property(get_rows)
