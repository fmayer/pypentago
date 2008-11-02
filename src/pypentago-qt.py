#!/usr/bin/env python
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


import sys
from PyQt4 import QtGui, QtCore

from pypentago import core


def get_coord(size, x):
    return int(x / size)


class Quadrant(QtGui.QLabel, core.Quadrant):
    def __init__(self, parent, uid):
        QtGui.QLabel.__init__(self, parent)
        core.Quadrant.__init__(self, uid)
        
        self.prnt = parent
        
        # If we use this in combination with spacers, we get a fixed-size
        # board, but the alignment problems will be gone.
        self.setMinimumSize(160, 160)
        self.setMouseTracking(True)
        
        # FIXME: Use real background image!
        # See http://www.bruylandt.com/pentago/pentago_17301026704340286.jpg
        self.bg_image = QtGui.QImage('bg.png')

        # Clockwise rotation image overlay.
        self.rot_cw = QtGui.QImage(
            'pypentago/client/img/rot_right.png'
        )

        # Counter-clockwise rotation image overlay.
        self.rot_ccw = QtGui.QImage(
            'pypentago/client/img/rot_left.png'
        )

        self.img = [
            QtGui.QImage(
                'pypentago/client/img/empty.png'
                ),
            QtGui.QImage(
                'pypentago/client/img/ball-white.png'
                ),
            QtGui.QImage(
                'pypentago/client/img/ball-black.png'
                ),
        ]

        self.rot_overlay = False

        self.zero_x = 0
        self.zero_y = 0

    def paintEvent(self, event):
        paint = QtGui.QPainter()
        paint.begin(self)

        zero_x = self.zero_x
        zero_y = self.zero_y

        h = self.height()
        w = self.width()
        min_size = min([h, w])
        
        # We might want to change that for performance reasons later on.        
        s_mode = QtCore.Qt.SmoothTransformation                
        
        # Resize the background image.
        bg = self.bg_image.scaledToHeight(min_size, s_mode)

        paint.drawImage(zero_x, zero_y, bg)

        # The size of one stone is a fourth of either the height or the
        # width of the quadrant, depending which of them is smaller.
        w_size = int(min_size / 4.0)
        # The space a stone has got is a third of the total space
        # available.
        size = int(min_size / 3.0)
        # What we need to add to compensate for the difference of the img
        # and the total size.
        d_size = (size - w_size) / 2.0
        # Scale all of the images to one fourth of the space we've got.
        # We're assuming to work with squared images!
        imgs = [img.scaledToHeight(w_size, s_mode) for img in self.img]

        # Yes yes, I know!
        r = xrange
        for y_c, y_p, row in zip(r(3), r(zero_y, 3 * size, size), self.field):
            for x_c, x_p, col in zip(r(3), r(zero_x, 3 * size, size), row):
                stone_value = self.field[y_c][x_c]
                paint.drawImage(x_p+d_size, y_p+d_size, imgs[stone_value])

        if self.rot_overlay:
            # Display rotation overlay.
            rot_cw = self.rot_cw.scaledToWidth(w / 2.0, s_mode)
            rot_ccw = self.rot_ccw.scaledToWidth(w / 2.0, s_mode)
            cw_y = h / 2.0 - rot_cw.height() / 2.0
            ccw_y = h / 2.0 - rot_ccw.height() / 2.0

            paint.drawImage(0, cw_y, rot_cw)
            paint.drawImage(w / 2.0, ccw_y, rot_ccw)

        # This was a triumph!
        paint.end()

    def rotate(self, clockwise=True):
        if clockwise:
            self.rotright()
        else:
            self.rotleft()
        self.prnt.may_rot = False
        # TODO: Write me!
        # This should animate the rotation.. If we manage to.
        print "Clockwise: %s" % clockwise

    def mousePressEvent(self, event):
        if self.prnt.may_rot and not self.rot_overlay:
            return
        x, y = event.x(), event.y()
        w = self.width()
        h = self.height()
        if self.rot_overlay:
            if x < w / 2.0:
                # Clockwise
                self.rotate(True)
            else:
                # Counterclockwise
                self.rotate(False)
            self.rot_overlay = False
            self.repaint()
            return
        size = int(min([h, w]) / 3.0)
        x, y = get_coord(size, x), get_coord(size, y)
        # try:
        #     self.game.set_stone(self.uid, y, x)
        # except (InvalidTurn, SquareNotEmpty):
        #     pass # Do something!
        self.set_stone(y, x, 1)
        
    def enterEvent(self, event):
        if self.prnt.may_rot:
            self.rot_overlay = True
        self.repaint()
    
    def leaveEvent(self, event):
        self.rot_overlay = False
        self.repaint()
    
    def set_stone(self, row, col, player_id):
        self.field[row][col] = player_id
        self.prnt.may_rot = True
        self.rot_overlay = True
        self.repaint()


class Board(QtGui.QWidget):
    def __init__(self, parent=None):
        # FIXME: Prevent quadrants from spreading out!
        QtGui.QWidget.__init__(self, parent)
        self.may_rot = False
        self.quadrants = [Quadrant(self, i) for i in xrange(4)]

        # Possible fix for spreading out. Limits board to fixed-size.
        hbox = QtGui.QHBoxLayout()
        vbox = QtGui.QVBoxLayout()
        # ---

        grid = QtGui.QGridLayout()
        grid.setSpacing(0)

        grid.addWidget(self.quadrants[0], 0, 0)
        grid.addWidget(self.quadrants[1], 0, 1)
        grid.addWidget(self.quadrants[2], 1, 0)
        grid.addWidget(self.quadrants[3], 1, 1)

        # Fix
        hbox.addLayout(grid)
        hbox.addStretch(0)

        vbox.addLayout(hbox)
        vbox.addStretch(0)
        self.setLayout(vbox)
        # --

        ##self.setLayout(grid)


class Game(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.board = Board(self)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.board, 0)
        
        self.player_list = QtGui.QListWidget()
        self.player_list.addItem("name")
        self.player_list.addItem("segfaulthunter")
        
        self.chat = QtGui.QListWidget()
        self.chat.addItem("<name> Hello!")
        self.chat.addItem("<segfaulthunter> Hello you!")
        
        self.chat_entry = QtGui.QLineEdit()
        
        sidebar = QtGui.QVBoxLayout()
        sidebar.addWidget(self.player_list, 20)
        sidebar.addWidget(self.chat, 40)
        sidebar.addWidget(self.chat_entry)
        
        hbox.addLayout(sidebar, 20)
        #hbox.addSpacing(1)
        self.setLayout(hbox)


class MainWindow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        game = Game(self)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(game)
        self.setLayout(hbox)
        self.setWindowTitle("Python Pentago")


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dt = MainWindow()
    dt.show()
    app.exec_()
