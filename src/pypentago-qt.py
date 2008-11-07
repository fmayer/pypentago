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

# TODO:
# Notificate about position(position flash)
# Visualize rotate(arrows popup + one flash)


import sys
import warnings
import time

from PyQt4 import QtGui, QtCore, QtSvg

from pypentago import core


def get_coord(size, x):
    return int(x / size)


class Overlay(QtCore.QObject):
    INIT_OPACITY = 0.1
    OPACITY_CHANGE = 0.05
    MAX_OPACITY = 0.6
    HOVER = 0.25
    def __init__(self, repaint):
        QtCore.QObject.__init__(self)
        self.value = self.INIT_OPACITY
        self.repaint = repaint
        self.shown = False
        self.add_cw = 0
        self.add_ccw = 0
        
        self.timer = QtCore.QTimer()
        self.timer.connect(self.timer, 
                           QtCore.SIGNAL('timeout()'),
                           self, QtCore.SLOT('tick()')
                           )
    
    def show(self):
        self.shown = True
        self.timer.start(100)
        
    def hide(self):
        self.value = self.INIT_OPACITY
        self.shown = False
        self.timer.stop()
    
    @QtCore.pyqtSignature('')
    def tick(self):
        if self.value >= self.MAX_OPACITY:
            self.timer.stop()
        else:
            self.value += self.OPACITY_CHANGE
        self.repaint()
    
    def __nonzero__(self):
        return self.shown
    
    def highlight_cw(self):
        self.add_cw = self.HOVER
        self.add_ccw = 0
    
    def highlight_ccw(self):
        self.add_ccw = self.HOVER
        self.add_cw = 0    
    
    @property
    def opacity(self):
        return self.value + self.add_cw, self.value + self.add_ccw


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
    PREVIEW_OPACITY = 0.4
    def __init__(self, parent, uid):
        QtGui.QLabel.__init__(self, parent)
        core.Quadrant.__init__(self, uid)
        
        self.prnt = parent
        
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
        
        self.overlay = Overlay(self.repaint)

        self.blink_timer = QtCore.QTimer(self)
        self.preview_stone = None
        self.user_control = True
        self.blink = []
    
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
        
        if self.preview_stone is not None:
            x_c, y_c = self.preview_stone
            x_p, y_p = x_c * size, y_c * size
            paint.setOpacity(self.PREVIEW_OPACITY)
            paint.drawImage(x_p+d_size, y_p+d_size, imgs[1])
            paint.setOpacity(1)
            
        if self.overlay:
            # Display rotation overlay.
            rot_cw = self.rot_cw.scaledToWidth(w / 2.0, s_mode)
            rot_ccw = self.rot_ccw.scaledToWidth(w / 2.0, s_mode)
            cw_y = h / 2.0 - rot_cw.height() / 2.0
            ccw_y = h / 2.0 - rot_ccw.height() / 2.0
            
            cw_o, ccw_o = self.overlay.opacity
            
            paint.setOpacity(cw_o)
            paint.drawPixmap(0, cw_y, rot_cw)
            if ccw_o != cw_o:
                paint.setOpacity(ccw_o)
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
        self.overlay.hide()
    
    @QtCore.pyqtSignature('')
    def blink_rot(self, what=None):
        # [var_name, min, max, step, add_]
        if what is not None:
            self.blink.append(what)
        
        for i, (name, min_, max_, step, add_) in enumerate(self.blink):
            if getattr(self, name) <= min_:
                self.blink[i][-1] = True
                add_ = True
            elif getattr(self, name) >= max_:
                self.blink[i][-1] = False
                add_ = False
            if add_:
                setattr(self, name, getattr(self, name) + step)
            else:
                setattr(self, name, getattr(self, name) - step)

        self.repaint()
        
        if not self.blink_timer.isActive():
            self.blink_timer = QtCore.QTimer(self)
            self.blink_timer.connect(self.blink_timer, 
                                     QtCore.SIGNAL('timeout()'),
                                     self, QtCore.SLOT('blink_rot()'))
            self.blink_timer.start(100)
            
    def show_rot(self, clockwise):
        self.user_control = False
        if clockwise:
            name = 'add_cw'
        else:
            name = 'add_cww'
        
        self.blink_rot([name, 0, 0.3, 0.04, True])
        self.fade_in()
        
    def mousePressEvent(self, event):
        if self.prnt.may_rot and not self.overlay:
            # This shouldn't actually be happening. Just in case it is.
            warnings.warn('may_rot == True and mousePressEvent but no overlay')
            return
        
        x, y = event.x(), event.y()
        w = self.width()
        h = self.height()
        
        if self.overlay:
            if x < w / 2.0:
                # Clockwise
                self.rotate(True)
            else:
                # Counter-clockwise
                self.rotate(False)
            self.repaint()
            # Update outdated position of preview stone.
            self.mouseMoveEvent(event)
        else:
            # No overlay. Player wants to set a stone.
            size = min([h, w]) / 3.0
            x, y = get_coord(size, x), get_coord(size, y)
            # try:
            #     self.game.set_stone(self.uid, y, x)
            # except (InvalidTurn, SquareNotEmpty):
            #     pass # Do something!
            self.set_stone(y, x, 1)
        
    def enterEvent(self, event):
        if self.prnt.may_rot:
            self.overlay.show()
        self.repaint()
    
    def leaveEvent(self, event):
        self.overlay.hide()
        self.preview_stone = None
        self.repaint()
    
    def mouseMoveEvent(self, event):
        if not self.overlay:
            x, y = event.x(), event.y()
            size = min([self.height(), self.width()]) / 3.0
            x, y = get_coord(size, x), get_coord(size, y)
            self.preview_stone = x, y
            self.repaint()
            return
        if not self.user_control:
            return
        
        x = event.x()
        if x < self.width() / 2.0:
            self.overlay.highlight_cw()
        else:
            self.overlay.highlight_ccw()
        self.repaint()
    
    def set_stone(self, row, col, player_id):
        self.field[row][col] = player_id
        self.prnt.may_rot = True
        self.overlay.show()
        self.repaint()


class Board(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.may_rot = False
        self.quadrants = [Quadrant(self, i) for i in xrange(4)]
    
    def paintEvent(self, event):
        size = min([self.height(), self.width()]) / 2.0
        
        for quad in self.quadrants:
            quad.resize(size, size)
        
        self.quadrants[0].move(0, 0)
        self.quadrants[1].move(0, size)
        self.quadrants[2].move(size, 0)
        self.quadrants[3].move(size, size)     
        

class Game(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.board = Board(self)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.board, 40)
        
        self.player_list = QtGui.QListWidget()
        self.player_list.addItem("name")
        self.player_list.addItem("segfaulthunter")
        
        self.chat = QtGui.QListWidget()
        self.add_msg('name', 'Hello!')
        self.add_msg('segfaulthunter', 'Hello you!')
        
        self.chat_entry = QtGui.QLineEdit()
        self.chat_entry.connect(self.chat_entry, 
                                QtCore.SIGNAL('returnPressed()'),
                                self,
                                QtCore.SLOT('send_msg()'))
        
        sidebar = QtGui.QVBoxLayout()
        sidebar.addWidget(self.player_list, 20)
        sidebar.addWidget(self.chat, 40)
        sidebar.addWidget(self.chat_entry)
        
        hbox.addLayout(sidebar, 25)
        #hbox.addSpacing(1)
        self.setLayout(hbox)
    
    @QtCore.pyqtSignature('')
    def send_msg(self):
        self.add_msg('name', self.chat_entry.text())
        self.chat_entry.clear()
        # TODO: Send to opponent.
    
    def add_msg(self, author, msg, utc_time=None):
        format = "[%(time)s] <%(author)s> %(msg)s"
        if utc_time is None:
            utc_time = time.time()
        time_ = time.strftime('%H:%M', time.localtime(utc_time))
        self.chat.addItem(format % dict(time=time_, author=author, msg=msg))
        self.chat.scrollToBottom()


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
