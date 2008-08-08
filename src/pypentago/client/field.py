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

import logging

log = logging.getLogger("pypentago.client.field")


class SubBoard(object):
    def __init__(self):
        pass
    
    def __get_value_list(self):
        value = []
        for row in self.grid:
            value.append([])
            for stone in row:
                value[-1].append(stone.value)
        return value
    
    def rotleft(self, evt=None):
        """
        Rotates the subboard no to the right
        """
        if (self.parent.conn.active and self.parent.set_stone) or evt == "conn":
            log.debug("In rotleft")
            field = self.__get_value_list()
            newfield = []
            for i in range(len(field)):
                newfield.append([])
                for k in range(3):
                    newfield[i].append(field[k][i])
            newfield.reverse()
            for (row, v_row) in zip(self.grid, newfield):
                for (stone, value) in zip(row, v_row):
                    stone.set_value(value)
            self.parent.rot_field = self.no
            self.parent.rot_dir = "L"
            self.Parent.send_turn()
    
    def rotright(self, evt=None):
        """
        Rotates the subboard no to the right
        """
        if (self.parent.conn.active and self.parent.set_stone) or evt == "conn":
            log.debug("In rotright")
            field = self.__get_value_list()
            newfield = []
            for i in range(len(field)):
                newfield.append([])
                for k in range(3):
                    newfield[i].append(field[2-k][2-i])
            newfield.reverse()
            for (row, v_row) in zip(self.grid, newfield):
                for (stone, value) in zip(row, v_row):
                    stone.set_value(value)
    
            self.parent.rot_field = self.no
            self.parent.rot_dir = "R"
            self.Parent.send_turn()

    def get_stone_value(self, row, col):
        return self.grid[row][col].value
    
    def set_opponent_stone(self, row, col):
        self.grid[row][col].set_opponent_stone()
    
    def set_own_stone(self, row, col):
        self.grid[row][col].set_own_stone()
    
class Game:
    def __init__(self):
        pass
    
    def set_opponent_stone(self, sub_board, row, col):
        self.games[sub_board].set_opponent_stone(row, col)
    
    def set_own_stone(self, sub_board, row, col):
        self.games[sub_board].set_own_stone(row, col)
    

if __name__ == "__main__":
    sub = SubBoard()
