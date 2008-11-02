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
from PyQt4 import QtGui, QtCore, QtSvg

from pypentago import core


def get_coord(size, x):
    return int(x / size)



class SVGFakeImage:
    def __init__(self, img):
        self.render = QtSvg.QSvgRenderer(img)
        self.cache = None
    
    def scaledToHeight(self, heigth, mode=None):
        if self.cache is not None and self.cache.height() == height:
            return self.cache
        viewbox = self.render.viewBox()
        h = viewbox.height()
        w = viewbox.width()
        
        ratio = w / float(h)
        
        new_h = heigth
        new_w = heigth * ratio
        
        img = QtGui.QPixmap(new_h, new_w)
        img.fill(QtCore.Qt.transparent)
        
        paint = QtGui.QPainter(img)
        
        self.render.render(paint)
        
        paint.end()
        self.cache = img
        return img

    def scaledToWidth(self, width, mode=None):
        if self.cache is not None and self.cache.width() == width:
            return self.cache
        viewbox = self.render.viewBox()
        h = viewbox.height()
        w = viewbox.width()
        
        ratio = h / float(w)
        
        new_w = width
        new_h = width * ratio
        
        img = QtGui.QPixmap(new_h, new_w)
        img.fill(QtCore.Qt.transparent)
        
        paint = QtGui.QPainter(img)
        
        self.render.render(paint)
        
        paint.end()
        self.cache = img
        return img



class Quadrant(QtGui.QLabel, core.Quadrant):
    INIT_OPACITY = 0.1
    OPACITY_CHANGE = 0.05
    MAX_OPACITY = 0.7
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
        self.rot_cw = SVGFakeImage(
            'pypentago/client/img/rot_cw.svg'
        )

        # Counter-clockwise rotation image overlay.
        self.rot_ccw = SVGFakeImage(
            'pypentago/client/img/rot_ccw.svg'
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
        self.overlay_opacity = self.INIT_OPACITY
        self.fade_timer = QtCore.QTimer(self)
        self.add_cw = self.add_ccw = 0

    def paintEvent(self, event):
        s_mode = QtCore.Qt.SmoothTransformation                

        h = self.height()
        w = self.width()
        min_size = min([h, w])
        
        rot_cw = self.rot_cw.scaledToWidth(w / 2.0, s_mode)
        rot_ccw = self.rot_ccw.scaledToWidth(w / 2.0, s_mode)
        
        paint = QtGui.QPainter()
        paint.begin(self)
        
        # We might want to change that for performance reasons later on.        
        
        # Resize the background image.
        bg = self.bg_image.scaledToHeight(min_size, s_mode)

        paint.drawImage(0, 0, bg)

        # The size of one stone is a fourth of either the height or the
        # width of the quadrant, depending which of them is smaller.
        w_size = min_size / 4.0
        # The space a stone has got is a third of the total space
        # available.
        size = min_size / 3.0
        # What we need to add to compensate for the difference of the img
        # and the total size.
        d_size = (size - w_size) / 2.0
        # Scale all of the images to one fourth of the space we've got.
        # We're assuming to work with squared images!
        imgs = [img.scaledToHeight(w_size, s_mode) for img in self.img]

        y_c = y_p = 0
        for row in self.field:
            x_c = x_p = 0
            for col in row:
                stone_value = self.field[y_c][x_c]
                paint.drawImage(x_p+d_size, y_p+d_size, imgs[stone_value])
                x_c += 1
                x_p += size
            y_c += 1
            y_p += size
        
        if self.rot_overlay:
            # Display rotation overlay.
            rot_cw = self.rot_cw.scaledToWidth(w / 2.0, s_mode)
            rot_ccw = self.rot_ccw.scaledToWidth(w / 2.0, s_mode)
            cw_y = h / 2.0 - rot_cw.height() / 2.0
            ccw_y = h / 2.0 - rot_ccw.height() / 2.0
            
            paint.setOpacity(self.overlay_opacity + self.add_cw)
            paint.drawPixmap(0, cw_y, rot_cw)
            if self.add_cw or self.add_ccw:
                paint.setOpacity(self.overlay_opacity + self.add_ccw)
            paint.drawPixmap(w / 2.0, ccw_y, rot_ccw)
            paint.setOpacity(1)

        # This was a triumph!
        paint.end()

    def rotate(self, clockwise=True):
        if clockwise:
            self.rotright()
        else:
            self.rotleft()
        
        self.prnt.may_rot = False
        self.rot_overlay = False
        self.fade_timer.stop()
        # TODO: Write me!
        # This should animate the rotation.. If we manage to.
        print "Clockwise: %s" % clockwise

    @QtCore.pyqtSignature('')
    def fade_in(self):
        self.rot_overlay = True
        if self.overlay_opacity >= self.MAX_OPACITY:
            if self.fade_timer.isActive():
                self.fade_timer.stop()
        else:
            self.overlay_opacity += self.OPACITY_CHANGE
            self.repaint()
        if not self.fade_timer.isActive():
            self.fade_timer = QtCore.QTimer(self)
            self.fade_timer.connect(self.fade_timer, QtCore.SIGNAL('timeout()'),
                                    self, QtCore.SLOT('fade_in()'))
            self.fade_timer.start(100)
        
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
                # Counter-clockwise
                self.rotate(False)
            self.repaint()
            return
        
        size = min([h, w]) / 3.0
        x, y = get_coord(size, x), get_coord(size, y)
        # try:
        #     self.game.set_stone(self.uid, y, x)
        # except (InvalidTurn, SquareNotEmpty):
        #     pass # Do something!
        self.set_stone(y, x, 1)
        
    def enterEvent(self, event):
        if self.prnt.may_rot:
            self.fade_in()
        self.repaint()
    
    def leaveEvent(self, event):
        self.rot_overlay = False
        self.fade_timer.stop()
        self.overlay_opacity = self.INIT_OPACITY
        self.repaint()
    
    def mouseMoveEvent(self, event):
        if not self.rot_overlay:
            return
        x, y = event.x(), event.y()
        if x < self.width() / 2.0:
            self.add_cw = 0.3
            self.add_ccw = 0
            self.repaint()
        else:
            self.add_ccw = 0.3
            self.add_cw = 0
            self.repaint()
    
    def set_stone(self, row, col, player_id):
        self.field[row][col] = player_id
        self.prnt.may_rot = True
        self.fade_in()
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
