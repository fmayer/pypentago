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


from PyQt4 import QtCore


class Blinker(QtCore.QObject):
    def __init__(self, min_, max_, step, add=True, init=0, 
                 callback=None, interval=100):
        QtCore.QObject.__init__(self)
        self.min_ = min_
        self.max_ = max_
        self._step = step
        self._add = add
        self.init = init
        self.value = init
        self.callback = callback
        self.interval = interval

        self.timer = QtCore.QTimer()
        self.timer.connect(self.timer, 
                           QtCore.SIGNAL('timeout()'),
                           self, QtCore.SLOT('tick()')
                           )
        self.s_shot = None
        self.active = False
    
    def get_step(self):
        # As this may change state of the iterator, 
        # it can't be made a property.
        if hasattr(self._step, 'next'):
            return self._step.next()
        elif hasattr(self._step, '__next__'):
            return self._step.__next__()
        else:
            return self._step
    
    def set_step(self, value):
        self._step = value
    
    def get_add(self, step=None):
        if step is None:
            step = self.get_step()
        
        if self.value + step > self.max_:
            self._add = False
        elif self.value - step < self.min_:
            self._add = True
        return self._add
    
    def set_add(self, value):
        self._add = value
    
    @QtCore.pyqtSignature('')
    def tick(self):
        step = self.get_step()
        if self.get_add(step):
            self.value += step
        else:
            self.value -= step
        if self.callback is not None:
            self.callback()
    
    def run(self, msec=None, callafter=None):
        self.active = True
        self.timer.start(self.interval)
        if callafter is not None:
            self.callafter = callafter
        if msec is not None:
            self.s_shot = QtCore.QTimer()
            self.s_shot.singleShot(msec, self.stop)
    
    @QtCore.pyqtSignature('')
    def stop(self):
        if self.active:
            self.active = False
            if self.s_shot is not None:
                self.s_shot.stop()
            self.on_stop()
            self.timer.stop()
    
    def on_stop(self):
        self.value = self.init
