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
import warnings
import time

import pypentago

from PyQt4 import QtGui, QtCore

from pypentago import core, CW, CCW
from pypentago.client import core as c_core
from pypentago.client.interface.blinker import Blinker
from pypentago.client.interface.svg import SVGFakePixmap


def get_coord(size, x):
    return int(x / size)


class OverlayBlink(Blinker):
    def __init__(self, overlay, repaint, callafter=None):
        Blinker.__init__(self, 0.2, 0.5, 0.05, callback=repaint)
        self.overlay = overlay
        self.callafter = callafter
    
    def run(self, msec=None, callafter=None):
        # Show overlay without fading in.
        self.overlay.value = 0.5
        self.overlay.shown = True
        Blinker.run(self, msec, callafter)
    
    def on_stop(self):
        # Hide overlay without stopping timer that wasn't started.
        self.overlay.value = self.overlay.INIT_OPACITY
        self.overlay.shown = False
        self.value = self.init
        self.callback()
        if self.callafter is not None:
            self.callafter()
    
    def __nonzero__(self):
        return self.timer.isActive()


class StoneBlink(Blinker):
    def __init__(self, repaint, callafter=None):
        Blinker.__init__(self, 0.4, 0.8, 0.05, callback=repaint)
        self.coord = None
        self.callafter = callafter

    def on_stop(self):
        self.value = self.init
        self.coord = None
        self.callback()
        if self.callafter is not None:
            self.callafter()
    
    def __nonzero__(self):
        return self.coord is not None and self.timer.isActive()


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


class Quadrant(QtGui.QLabel, core.Quadrant):
    PREVIEW_OPACITY = 0.4
    def __init__(self, parent, uid):
        QtGui.QLabel.__init__(self, parent)
        core.Quadrant.__init__(self, uid)
        
        self.prnt = parent
        
        self.setMouseTracking(True)
        
        # FIXME: Use real background image!
        # See http://tinyurl.com/pboard
        self.bg_image = QtGui.QImage(
            pypentago.data['quad_bg.png']
        )
        
        # 0 1 | With 0 aligned properly, 
        # 2 3 | 1 and 3 need to be mirrored horizontally, 2 and 3 verticaly.
        # While horizontally mirror means "| *" -> "* |", meaning that the
        # mirror axis lies vertically.
        self.bg_image = self.bg_image.mirrored(uid == 1 or uid == 3,
                                               uid == 2 or uid == 3)

        # Clockwise rotation image overlay.
        self.rot_cw = SVGFakePixmap(
            pypentago.data['rot_cw.svg']
        )

        # Counter-clockwise rotation image overlay.
        self.rot_ccw = SVGFakePixmap(
            pypentago.data['rot_ccw.svg']
        )
        

        self.img = [
            QtGui.QImage(
                pypentago.data['empty.png']
                ),
            QtGui.QImage(
                pypentago.data['ball-white.png']
                ),
            QtGui.QImage(
                pypentago.data['ball-black.png']
                ),
        ]
        
        self.overlay = Overlay(self.repaint)

        self.blink_timer = QtCore.QTimer(self)
        self.preview_stone = None
        self.blink_cw = OverlayBlink(self.overlay, self.repaint)
        self.blink_ccw = OverlayBlink(self.overlay, self.repaint)
        self.blink_stone = StoneBlink(self.repaint)
        self.block_user_control = [self.blink_ccw, self.blink_cw,
                                   self.blink_stone]
    
    def paintEvent(self, event):
        # We might want to change that for performance reasons later on.
        # Either FastTransformation or SmoothTransformation.
        s_mode = QtCore.Qt.SmoothTransformation                
        
        h = self.height()
        w = self.width()
        min_size = min([h, w])
        
        paint = QtGui.QPainter()
        paint.begin(self)
        
        # Resize the background image.
        bg = self.bg_image.scaledToHeight(min_size, s_mode)
        
        paint.drawImage(0, 0, bg)
        
        s_size = min_size - min_size / 6.0
        
        # The space a stone has got is a third of the total space
        # available.
        size = s_size / 3.0
        # The size of one stone is a fourth of either the height or the
        # width of the quadrant, depending which of them is smaller.
        w_size = size / 1.25
        # What we need to add to compensate for the difference of the img
        # and the total size.
        d_size = (size - w_size) / 2.0 + (min_size - s_size) / 2.0
        # Scale all of the images to one fourth of the space we've got.
        # We're assuming to work with squared images!
        imgs = [img.scaledToHeight(w_size, s_mode) for img in self.img]
        
        if self.blink_stone:
            b_col, b_row = self.blink_stone.coord
        else:
            b_col, b_row = None, None
        
        for y_c, row in enumerate(self.field):
            y_p = y_c * size
            for x_c, col in enumerate(row):
                x_p = x_c * size
                if x_c == b_col and y_c == b_row:
                    paint.setOpacity(self.blink_stone.value)
                stone_value = self.field[y_c][x_c]
                paint.drawImage(x_p+d_size, y_p+d_size, imgs[stone_value])
                if x_c == b_col and y_c == b_row:
                    paint.setOpacity(1)
        
        if self.preview_stone is not None:
            x_c, y_c = self.preview_stone
            if not self.field[y_c][x_c]:
                uid = self.prnt.prnt.local_player.uid
                x_p, y_p = x_c * size, y_c * size
                paint.setOpacity(self.PREVIEW_OPACITY)
                paint.drawImage(x_p+d_size, y_p+d_size, imgs[uid])
                paint.setOpacity(1)
            
        if self.overlay:
            # Display rotation overlay.
            rot_cw = self.rot_cw.scaledToWidth(w / 2.0, s_mode)
            rot_ccw = self.rot_ccw.scaledToWidth(w / 2.0, s_mode)
            cw_y = h / 2.0 - rot_cw.height() / 2.0
            ccw_y = h / 2.0 - rot_ccw.height() / 2.0
            
            cw_o, ccw_o = self.overlay.opacity
            
            paint.setOpacity(cw_o + self.blink_cw.value)
            paint.drawPixmap(0, cw_y, rot_cw)
            if ccw_o != cw_o or self.blink_ccw or self.blink_cw:
                paint.setOpacity(ccw_o + self.blink_ccw.value)
            paint.drawPixmap(w / 2.0, ccw_y, rot_ccw)
            paint.setOpacity(1)
        
        # This was a triumph!
        paint.end()

    def rotate(self, clockwise, user_done=True):
        core.Quadrant.rotate(self, clockwise)
        
        self.prnt.may_rot = False
        self.overlay.hide()
        self.repaint()
        if user_done:
            self.prnt.do_turn(clockwise and CW or CCW, self.uid)
            
    def show_rot(self, clockwise, callafter=None):
        if clockwise:
            self.blink_cw.run(5000, callafter)
        else:
            self.blink_ccw.run(5000, callafter)
    
    def show_loc(self, col, row, callafter=None):
        self.blink_stone.coord = (col, row)
        self.blink_stone.run(5000, callafter)
    
    def mousePressEvent(self, event):
        if not self.prnt.user_control:
            self.prnt.reclaim_control()
            return
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
            self.set_stone(y, x)
        
    def enterEvent(self, event):
        if self.prnt.may_rot:
            self.overlay.show()
        self.repaint()
    
    def leaveEvent(self, event):
        if not (self.blink_ccw or self.blink_cw):
            self.overlay.hide()
        self.preview_stone = None
        self.repaint()
    
    def mouseMoveEvent(self, event):
        if not self.prnt.user_control:
            return
        
        if not self.overlay:
            x, y = event.x(), event.y()
            size = min([self.height(), self.width()]) / 3.0
            x, y = get_coord(size, x), get_coord(size, y)
            self.preview_stone = x, y
            self.repaint()
            return
        else:
            x = event.x()
            if x < self.width() / 2.0:
                self.overlay.highlight_cw()
            else:
                self.overlay.highlight_ccw()
            self.repaint()
    
    def set_stone(self, row, col, player_id=None, may_rot=True):
        if player_id is None:
            player_id = self.prnt.prnt.local_player.uid
        if self.field[row][col]:
            return
        self.field[row][col] = player_id
        self.prnt.may_rot = may_rot
        self.prnt.temp_turn = [self.uid, row, col]
        if may_rot:
            self.overlay.show()
        self.repaint()
    
    @property
    def user_control(self):
        return not any(self.block_user_control)
    
    def reclaim_control(self):
        for elem in self.block_user_control:
            if elem:
                elem.stop()


class Board(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.temp_turn = None
        self.prnt = parent
        self.may_rot = False
        self.quadrants = [Quadrant(self, i) for i in xrange(4)]
        # Demonstration:
        ## self[1].set_stone(1, 1, 1, False)
        ## self.show_turn(1, 0, 1, 1, 1, True)
    
    def do_turn(self, rot_dir, rot_quad):
        if self.temp_turn is None:
            raise ValueError('No turn stored!')
        self.prnt.local_player.do_turn(self.temp_turn + [rot_dir, rot_quad])
        self.temp_turn = None
    
    def paintEvent(self, event):
        size = min([self.height(), self.width()]) / 2.0
        
        for quad in self.quadrants:
            quad.resize(size, size)
        
        self.quadrants[0].move(0, 0)
        self.quadrants[1].move(size, 0)
        self.quadrants[2].move(0, size)
        self.quadrants[3].move(size, size)
    
    def show_turn(self, p_id, s_quad, row, col, r_quad, clockwise):
        rot = lambda: self[r_quad].rotate(clockwise, False)
        self[s_quad].set_stone(row, col, p_id, False)
        self[s_quad].show_loc(col, row,
                              lambda: self[r_quad].show_rot(clockwise, rot)
                      )
    
    def __getitem__(self, i):
        return self.quadrants[i]
    
    @property
    def user_control(self):
        return (self.prnt.local_player.is_turn() and
                all(x.user_control for x in self.quadrants))
    
    def reclaim_control(self):
        if not self.prnt.local_player.is_turn():
            # It's not our turn. We can't reclaim user control.
            return
        
        for quad in self.quadrants:
            if not quad.user_control:
                quad.reclaim_control()
        

class Game(QtGui.QWidget):
    def __init__(self, game, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.prnt = parent
        self.board = Board(self)
        self.game = game
        self.local_player = c_core.LocalPlayer(self)
        self.game.add_player(self.local_player)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.board, 40)
        
        self.player_list = QtGui.QListWidget()
        self.player_list.addItem("Player 1")
        self.player_list.addItem("Player 2")
        
        self.chat = QtGui.QListWidget()
        
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
        self.local_player.send_msg(self.chat_entry.text())
        self.chat_entry.clear()
    
    def add_msg(self, author, msg, utc_time=None):
        format = "[%(time)s] <%(author)s> %(msg)s"
        if utc_time is None:
            utc_time = time.time()
        time_ = time.strftime('%H:%M', time.localtime(utc_time))
        self.chat.addItem(format % dict(time=time_, author=author, msg=msg))
        self.chat.scrollToBottom()
    
    def quit(self):
        self.local_player.quit_game()
    
    def close_window(self):
        self.prnt.close()


class GameWindow(QtGui.QWidget):
    def __init__(self, game, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.game = Game(game, self)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.game)
        self.setLayout(hbox)
        self.setWindowTitle("Python Pentago Game")
        self.setWindowIcon(
            QtGui.QIcon(pypentago.data['icon.png'])
        )
        self.resize(750, 480)
    
    def closeEvent(self, event):
        self.game.quit()
