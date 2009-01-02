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

from PyQt4 import QtSvg, QtCore, QtGui


class SVGFakePixmap:
    def __init__(self, img):
        self.render = QtSvg.QSvgRenderer(img)
        self.cache = None
    
    def scaledToHeight(self, height, mode=None):
        if self.cache is not None and self.cache.height() == height:
            return self.cache
        viewbox = self.render.viewBox()
        h = viewbox.height()
        w = viewbox.width()
        
        ratio = w / float(h)
        
        new_h = height
        new_w = height * ratio
        
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
