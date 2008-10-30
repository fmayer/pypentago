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
import wx

import actions

from os.path import join
from pypentago.client import context


# TODO: Find out how to make the field for the icon just as big as needed
class StatusBar(wx.StatusBar, actions.ActionHandler):
    _decorators = []
    def __init__(self, parent, imgpath):
        wx.StatusBar.__init__(self, parent)
        actions.ActionHandler.__init__(self, context.gui)
        self.log = logging.getLogger("pypentago.interface.statusbar")
        self.imgpath = imgpath
        self.SetFieldsCount(2)
        self.SetStatusText('Welcome to pyPentago. Visit #pypentago'
                           ' @ irc.freenode.net', 0)
        self.SetStatusWidths([-15, -1])
        self._icon = wx.StaticBitmap(self, -1, wx.Bitmap(join(imgpath, 
                                                        "status_orange.png")))
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.PlaceIcon()
    
    @context.register_method('turn_recv', _decorators)
    def SetGreen(self, state=None):
        self.log.debug("[SetGreen]")
        self.icon_file = "status_green.png"

    @context.register_method('turn_sent', _decorators)
    def SetYellow(self, state=None):
        self.log.debug("[SetYellow]")
        self.icon_file = "status_yellow.png"

    def SetOrange(self):
        self.log.debug("[SetOrange]")
        self.icon_file = "status_orange.png"

    def SetRed(self):
        self.log.debug("[SetRed]")
        self.icon_file = "status_red.png"

    def PlaceIcon(self):
        rect = self.GetFieldRect(1)
        self._icon.SetPosition((rect.x+3, rect.y+3))
    
    def SetIcon(self, image_file):
        self._icon.Destroy()
        self._icon = wx.StaticBitmap(self, -1, wx.Bitmap(join(self.imgpath, 
                                                              image_file)))
        self.PlaceIcon()    

    def GetIcon(self):
        return self._icon

    def OnSize(self, event):
        self.PlaceIcon()

    icon_file = property(GetIcon, SetIcon)
