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

""" This module provides a Panel and a Frame to view pyPentago replays """

if __name__ == "__main__":
    # Sets the PYTHONPATH if the file is not used as a module.
    from os.path import abspath, dirname, join
    import sys
    script_path = abspath(dirname(__file__))
    sys.path.append(abspath(join(script_path, "..", '..')))

import wx
import wx.lib.buttonpanel as bp
from pypentago.client.interface import SubBoard
from pypentago.pgn import parse_file

class Controls(wx.Panel):
    """ The controls for the replay. Contains next/previous turn and apply 
    rotating so players have a clear impression of where the stone was set and 
    what quadrant was rotated which way """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        
class ReplayBoardPanel(wx.Panel):
    """ The actual board containing the game """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.games = []
        for elem in range(4):
            self.games.append(SubBoard(self, elem))
        sizer = wx.GridSizer(2, 2, 0, 0)
        for game in self.games:
            sizer.Add(game, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)

class ReplayPanel(wx.Panel):
    """ The master panel """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        
        self.turns = []
        self.current_turn = 0
        self.rotated = False
        
        self.controls = Controls(self)
        self.board = ReplayBoardPanel(self)
        sizer = wx.BoxSizer()
        sizer.Add(self.controls)
        sizer.Add(self.board)
        self.SetSizer(sizer)

class ReplayFrame(wx.Frame):
    """ The frame for the replay viewer when run standalone """
    def __init__(self):
        wx.Frame.__init__(self, None,  -1, "pyPentago replay viewer", 
                          size=(760, 810))
        self.panel = ReplayPanel(self)
        self.make_menu()
    def make_menu(self):
        """ Create the menu for the mainframe. Incorporate into 
        pypentago.client.interface.MainFrame once this module is done and 
        ReplayPanel is embedded into the main pypentago window """
        menu_bar = wx.MenuBar()
        
        file_menu = wx.Menu()
        self.open_file = file_menu.Append(-1, "&Open\tCtrl-O")
        
        menu_bar.Append(file_menu, "&File")
        
        self.Bind(wx.EVT_MENU, self.on_open, self.open_file)
        
        self.SetMenuBar(menu_bar)
        
    def on_open(self, evt):
        """ Show a file dialog and parse the file selected """
        dlg = wx.FileDialog(self, "Select the replay file you want to review", 
                            wildcard="PGN files (*.pgn)|*.pgn|"
                            "All files (*)|*")
        if dlg.ShowModal() == wx.ID_OK:
            self.panel.turns = parse_file(dlg.Path)

def main():
    """ Function that is run when the file is executed on its own """
    app = wx.PySimpleApp()
    main_frame = ReplayFrame()
    main_frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()