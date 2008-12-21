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

from pypentago import core, CW, CCW

class LocalPlayer(core.Player):
    def __init__(self, gui_game):
        core.Player.__init__(self)
        self.gui_game = gui_game
    
    def display_turn(self, p, turn):
        quad, row, col, rot_dir, r_quad = turn
        self.gui_game.board.show_turn(p.uid, quad, row, col, r_quad,
                                      rot_dir == CW)
