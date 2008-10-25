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

import sys
import wx
import logging


if __name__ == '__main__':
    print "Please run main.py to run the program"
    sys.exit(2)


from os.path import dirname, join
from webbrowser import open as browser_open

from wx.aui import AuiNotebook
from wx.lib.buttons import GenBitmapButton
from wx.lib.mixins.listctrl import ColumnSorterMixin
from wx.lib.wordwrap import wordwrap

from pypentago import client, actions, IMGPATH
from pypentago import __version__, __authors__, __copyright__, __url__
from pypentago import __artists__, __description__, __bugs__

from pypentago.get_conf import get_conf_obj
from pypentago.pgn import from_pgn, to_pgn, write_file, InvalidPGN

from pypentago.client import field
from pypentago.client import connection

from pypentago.client.interface.display_player import DisplayPlayerFrame
from pypentago.client.interface.gamelist import ListGames
from pypentago.client.interface.statusbar import StatusBar
from pypentago.client.interface.user_wizard import run_wizard

from pypentago.client.connection import run_client

from pypentago.exceptions import SquareNotEmpty


script_path = dirname(__file__)
imgpath = join(script_path, '..', "img")
log = logging.getLogger("pypentago.interface")


class ChangePwdDialog(wx.Dialog):
    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, "Enter old password"), 
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.old_pwd = wx.TextCtrl(self, -1, style=wx.PASSWORD)
        self.new_pwd = wx.TextCtrl(self, -1, style=wx.PASSWORD)
        sizer.Add(self.old_pwd, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        sizer.Add(wx.StaticText(self, -1, "Enter new password"), 
                  flag=wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.new_pwd, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        okay_button = wx.Button(self, wx.ID_OK, "OK")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")
        okay_button.SetDefault()
        button_sizer.Add(okay_button, flag=wx.ALIGN_CENTER)
        button_sizer.Add(cancel_button, flag=wx.ALIGN_CENTER)
        sizer.Add(button_sizer)
        self.SetSizer(sizer)
        self.Fit()
        self.old_pwd.SetFocus()


class NewGameDialog(wx.Dialog):
    def __init__(self, parent, text, title):
        wx.Dialog.__init__(self, parent, -1, title)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, text), 
                  flag=wx.ALIGN_CENTER_VERTICAL)
        self.game_name = wx.TextCtrl(self, -1)
        self.game_ranked = wx.CheckBox(self, -1, "Ranked game")
        sizer.Add(self.game_name, flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        sizer.Add(self.game_ranked, flag=wx.ALIGN_CENTER_VERTICAL)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        okay_button = wx.Button(self, wx.ID_OK, "OK")
        cancel_button = wx.Button(self, wx.ID_CANCEL, "Cancel")
        okay_button.SetDefault()
        button_sizer.Add(okay_button, flag=wx.ALIGN_CENTER)
        button_sizer.Add(cancel_button, flag=wx.ALIGN_CENTER)
        sizer.Add(button_sizer)
        self.SetSizer(sizer)
        self.Fit()
        self.game_name.SetFocus()


class Square(wx.BitmapButton):
    def __init__(self, parent, stone):
        self.value = 0
        self.stone = stone
        self.create_colours()
        
        wx.BitmapButton.__init__(self, parent, -1, self.empty)
        self.game = self.Parent.Parent
        self.Bind(wx.EVT_BUTTON, self.on_clicked)
    
    def on_clicked(self, evt):
        if self.game.conn.active:
            log.debug("Applying turn")
            self.set_own_stone()
        else:
            log.debug("Not your turn")
    
    def create_colours(self):
        self.empty = wx.Image(join(imgpath, "empty.png"), 
                              wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.black = wx.Image(join(imgpath, "ball-black.png"), 
                              wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.white = wx.Image(join(imgpath, "ball-white.png"), 
                              wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.colours = [self.empty, self.white, self.black]
    
    def set_own_stone(self):
        if not self.value and not client.gui_current_game.set_stone:
            self.value = 1
            self.SetBitmapLabel(self.white)
            self.game.set_stone = (self.Parent.no, self.stone[0], 
                                            self.stone[1])
            self.game.set_stone_button = self
        else:
            self.update()
            raise SquareNotEmpty
    
    def set_opponent_stone(self):
        if not self.value:
            self.value = 2
            self.SetBitmapLabel(self.black)
        else:
            self.update()
            raise SquareNotEmpty
    
    def update(self, evt=None):
        self.SetBitmapLabel(self.colours[self.value])
    
    def set_value(self, value):
        self.value = value
        self.update()


class SubBoard(wx.Panel, field.SubBoard):
    def __init__(self, parent, no):
        wx.Panel.__init__(self, parent)
        
        self.no = no
        self.parent = parent
        
        self.create_grid()
        self.create_sizer()

    def create_rot_buttons(self):
        return [wx.Image(join(imgpath, img), wx.BITMAP_TYPE_ANY) 
                for img in ('rot_left.png', 'rot_right.png')]
    
    def create_sizer(self):
        # Consider splitting the following function in multiple, shorter ones.
        self.main_sizer = wx.GridBagSizer()
        square_sizer = wx.GridBagSizer()
        
        for row in self.grid:
            for square in row:
                square_sizer.Add(square, pos = square.stone)
        
        rot_left, rot_right = self.create_rot_buttons()
        
        box = wx.StaticBox(self)
        statboxsizer = wx.StaticBoxSizer(box)
        statboxsizer.Add(square_sizer)#, 0, wx.ALL | wx.EXPAND, 5)
        
        # Rotate 90 degrees to the right
        right = (True, )
        # Rotate 90 degrees to the left
        left = (False, )
        # Rotate 180 degrees
        half_rot = (True, True)
        
        if self.no == 0:
            rotation = (right, half_rot)
            widget_pos = ((0, 1), (1, 0), (1, 1))
        elif self.no == 1:
            rotation = (right, None)
            widget_pos = ((0, 0), (1, 1), (1, 0))
        elif self.no == 2:
            rotation = (left, half_rot)
            widget_pos = ((1, 1), (0, 0), (0, 1))
        elif self.no == 3:
            rotation = (left, None)
            widget_pos = ((1, 0), (0, 1), (0, 0))

        widgets = [] 
        for img, rot in zip((rot_left, rot_right), rotation):
            if not rot is None:
                for elem in rot:
                    img = img.Rotate90(elem)
            widgets.append(wx.BitmapButton(self, -1, img.ConvertToBitmap()))
        widgets.append(statboxsizer)
            
        for widget, pos in zip(widgets, widget_pos):
            self.main_sizer.Add(widget, pos, flag = wx.ALL | wx.EXPAND)
        
        self.rot_left_button, self.rot_right_button, statboxsizer = widgets
        
        self.rot_left_button.Bind(wx.EVT_BUTTON, self.rotleft)
        self.rot_right_button.Bind(wx.EVT_BUTTON, self.rotright)
        
        self.SetSizer(self.main_sizer)

    def create_grid(self):
        self.grid = []
        for row in range(3):
            self.grid.append([])
            for col in range(3):
                self.grid[-1].append(Square(self, (row, col)))


class Welcome(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        welcome = wx.TextCtrl(self, -1, "Welcome to pyPentago", 
                              style = wx.TE_MULTILINE | wx.TE_READONLY)
        sizer = wx.BoxSizer()
        sizer.Add(welcome, 1, wx.EXPAND)
        self.SetSizer(sizer)


class Game(wx.Panel, field.Game, actions.ActionHandler):
    _decorators = []
    def __init__(self, parent, conn=False):
        wx.Panel.__init__(self, parent)
        actions.ActionHandler.__init__(self)
        
        self.parent = parent
        self.games = []
        self.set_stone = False        
        self.rot_dir = False
        self.rot_field = False
        self.conn = conn
        self.set_stone_button = False
        self.turn_log = []
        for elem in range(4):
            self.games.append(SubBoard(self, elem))
        sizer = wx.GridSizer(2, 2, 0, 0)
        for game in self.games:
            sizer.Add(game, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer)
    
    def undo(self, evt=None):
        log.debug("Attempting undo")
        if self.set_stone_button:
            log.debug("Undo possible")
            self.set_stone_button.set_value(0)
            self.set_stone = False
            self.set_stone_button = False
    
    def apply_own_turn(self, turn):
        field, row, position, rot_dir, rot_field = turn
        log.debug(field, row, position, rot_dir, rot_field)
        self.set_own_stone(int(field), int(row), int(position))
        if rot_dir == "R":
            log.debug("Rotating right in applyOwnTurn")
            self.games[int(rot_field)].rotright()
        if rot_dir == "L":
            self.games[int(rot_field)].rotleft()
            log.debug("Rotating left in applyOwnTurn")
        self.active = False
    
    @actions.register_method('turn_recv', _decorators)
    def apply_opponent_turn(self, turn):
        field, row, position, rot_dir, rot_field = turn
        self.set_opponent_stone(int(field), int(row), int(position))
        if rot_dir == "R":
            log.debug("Rotating right in applyOpponentTurn")
            self.games[int(rot_field)].rotright("conn")
        if rot_dir == "L":
            self.games[int(rot_field)].rotleft("conn")
            log.debug("Rotating left in applyOpponentTurn")
        self.active = True

    def save_replay(self, evt=None):
        file_name_dia = wx.FileDialog(self, "Select file to save replay in", 
                                      style=wx.SAVE)
        if file_name_dia.ShowModal() == wx.ID_OK:
            write_file(self.turn_log, file_name_dia.GetPath())
    
    def send_turn(self):
        if self.conn.active:
            turn = self.set_stone + (self.rot_dir, self.rot_field)
            
            self.turn_log.append(turn)  
            self.conn.do_turn(*turn)
            
            self.set_stone = False
            self.rot_dir = False
            self.rot_field = False
            self.conn.active = False
            self.set_stone_button = False
            
            actions.emmit_action('turn_sent')


class Ladder(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)


class Login(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.name = wx.TextCtrl(self)
        self.passwd = wx.TextCtrl(self, style = wx.TE_PASSWORD |
                                  wx.TE_PROCESS_ENTER)
        execute = wx.Button(self, -1, "Login")
        self.text = wx.StaticText(self)
        
        sizer.Add(self.name, flag = wx.ALIGN_CENTRE) 
        sizer.Add(self.passwd, flag = wx.ALIGN_CENTRE)
        sizer.Add(execute, flag = wx.ALIGN_CENTRE)
        sizer.Add(self.text, flag = wx.ALIGN_CENTRE)


        self.SetSizer(sizer)
        execute.Bind(wx.EVT_BUTTON, self.on_execute)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_execute, self.passwd)
        
        self.name.SetFocus()
    
    def on_execute(self, evt):
        self.parent.conn.login(self.name.GetValue(), self.passwd.GetValue())


class MainPanel(wx.Panel, actions.ActionHandler):
    _decorators = []
    def __init__(self, parent, server, port):
        wx.Panel.__init__(self, parent, -1)
        actions.ActionHandler.__init__(self)
        
        self.tabs = AuiNotebook(self)
        self.status_bar = parent.status_bar
        run_client(server, port)
        self.conn = False
        self.login = Login(self)
        self.tabs.AddPage(self.login, "Login")
        self.list_games = ListGames(self)
        self.tabs.AddPage(self.list_games,  "List Games")
        sizer = wx.BoxSizer()
        sizer.Add(self.tabs, 1, wx.EXPAND)
        self.SetSizer(sizer)

    @actions.register_method('conn_established', _decorators)
    def connection_established(self, state):
        self.conn = state
        
        self.Parent.open_game.Enable(True)
        self.Parent.create_account.Enable(True)
    
    @actions.register_method('registered', _decorators)
    def registration(self, ret_code):
        if ret_code == connection.ID_REG:
            # Registration successful
            wx.MessageBox('Registration successful.')
        elif ret_code == connection.ID_NOT_REG:
            # Registration failed
            wx.MessageBox('Registration failed!')
        elif ret_code == connection.ID_DUP:
            wx.MessageBox("The name you tried to register is not available "
              "anymore. \nIf you are using an unmodified client you "
              "should report this as it is a bug in the registration "
              "wizard", "Login required")    
    
    @actions.register_method('login', _decorators)
    def logged_in(self, logged_in=True):
        if logged_in:
            log.info("Logged in")
            self.tabs.RemovePage(self.tabs.GetPageIndex(self.login))
        else:
            self.login.text.Label = "Error logging in"
            self.login.text.CentreOnParent(wx.HORIZONTAL)
            log.info("Error logging in")
    
    @actions.register_method('conn_lost', _decorators)
    def conn_lost(self, ranked=False):
        if ranked:
            appendix = "\nThis will count as a win for you"
        else:
            appendix = ""
        wx.MessageBox("The connection of your opponent dropped.%s" % appendix, 
                      "Game Over", wx.OK | wx.ICON_EXCLAMATION)
        self.game_over()
    
    @actions.register_method('display_player', _decorators)
    def display_player(self, player):
        new_frame = DisplayPlayerFrame(player)
        new_frame.Show()
    
    @actions.register_method('game_over', _decorators)
    def game_over(self, outcome=None):
        """ Things to be executed after a game is over no matter if the local 
        player has lost or won it. """
        if outcome == connection.ID_LOST:
            text = "You won the game"
        elif outcome == connection.ID_WIN:
            text = "You lost the game"
        elif outcome == connection.ID_DRAW:
            text = "The game was a draw"
        else:
            text = "The game ended unexpectedly"
        wx.MessageBox(text, "Game Over", wx.OK | wx.ICON_INFORMATION)
        
        self.Parent.close_game.Enable(False)
        self.Parent.undo.Enable(False)
        self.Parent.apply_pgn.Enable(False)
        
        # Clean up any handlers so they do not receive events for the next
        # game.
        self.game.remove_handlers()
        try:
            self.tabs.RemovePage(self.tabs.GetPageIndex(self.game))
        except ValueError:
            log.error("Could not close game tab")
    
    @actions.register_method('not_logged_in', _decorators)
    def not_logged_in(self, state=None):
        wx.MessageBox("This functionality needs you to log in", 
                      "Login required")
    
    @actions.register_method('start', _decorators)
    def start_game(self, beginner=False):
        self.game = Game(self, self.conn)
        client.gui_current_game = self.game # Make it easier to access the 
                                            # current GUI game object.
        self.tabs.AddPage(self.game, "Game")
        if not beginner:
            self.opponent_turn()
        else:
            self.your_turn()
            
    @actions.register_method('turn_recv', _decorators)
    def your_turn(self, state=None):
        """ GUI things to be executed when it's the local players' turn """
        self.Parent.RequestUserAttention()
        
        self.status_bar.SetStatusText("Your turn.")
        self.status_bar.SetGreen()
        
        self.Parent.undo.Enable(True)
        self.Parent.apply_pgn.Enable(True)
        self.Parent.save_replay.Enable(True)
    
    @actions.register_method('turn_sent', _decorators)
    def opponent_turn(self, state=None):
        """ GUI things to be executed when it's the opponents turn """
        self.status_bar.SetRed()
        self.status_bar.SetStatusText("Opponents turn.")
        
        self.Parent.undo.Enable(False)
        self.Parent.apply_pgn.Enable(False)


class MainFrame(wx.Frame):
    def __init__(self, server, port):
        wx.Frame.__init__(self, None,  -1, "pyPentago", size=(760, 810))
        self.SetIcon(wx.Icon(join(imgpath, "icon.png"), wx.BITMAP_TYPE_ANY))
        self.status_bar = StatusBar(self, imgpath)
        self.SetStatusBar(self.status_bar)
        self.panel = MainPanel(self, server, port)
        self.make_menu()
        self.status_bar.SetRed()

        
    def make_menu(self):
        menu_bar = wx.MenuBar()
        
        operations_menu = wx.Menu()
        self.open_game = operations_menu.Append(-1, "&Open Game\tCtrl-N")
        self.close_game = operations_menu.Append(-1, "&Close Game")
        self.create_account = operations_menu.Append(-1, "Create &Account")
        self.change_pwd = operations_menu.Append(-1, "Change &Password")
        wx_menu_exit = operations_menu.Append(-1, "E&xit Application")

        help_menu = wx.Menu()
        about = help_menu.Append(-1, "&About")
        bug_tracker = help_menu.Append(-1, "&Bug Tracker")
        
        game_menu = wx.Menu()
        self.undo = game_menu.Append(-1, "&Undo\tCtrl-Z")
        self.apply_pgn = game_menu.Append(-1, "&Apply Turn\tCtrl-T")
        self.save_replay = game_menu.Append(-1, "&Save Replay")
               
        self.open_game.Enable(False)
        self.close_game.Enable(False)
        self.create_account.Enable(False)
        self.undo.Enable(False)
        self.apply_pgn.Enable(False)
        self.save_replay.Enable(False)
        
        menu_bar.Append(operations_menu, "&Operations")
        menu_bar.Append(game_menu, "&Game")
        menu_bar.Append(help_menu, "&Help")
        
        self.SetMenuBar(menu_bar)
        
        self.Bind(wx.EVT_MENU, self.on_open_game, self.open_game)
        self.Bind(wx.EVT_MENU, self.on_close_game, self.close_game)
        self.Bind(wx.EVT_MENU, self.on_change_passwd, self.change_pwd)
        self.Bind(wx.EVT_MENU, self.on_menu_exit, wx_menu_exit)
        self.Bind(wx.EVT_MENU, self.on_about, about)
        self.Bind(wx.EVT_MENU, self.on_bug_tracker, bug_tracker)
        self.Bind(wx.EVT_MENU, self.on_create_acc, self.create_account)
        self.Bind(wx.EVT_MENU, self.on_undo, self.undo)
        self.Bind(wx.EVT_MENU, self.on_apply_pgn, self.apply_pgn)
        self.Bind(wx.EVT_MENU, self.on_save_replay, self.save_replay)
    
    def on_change_passwd(self, evt):
        dlg = ChangePwdDialog(self, "Require password")
        if dlg.ShowModal() == wx.ID_OK:
            old_pwd = dlg.old_pwd.Value
            new_pwd = dlg.new_pwd.Value
            self.panel.conn.change_password(old_pwd, new_pwd)
    
    def on_save_replay(self, evt):
        self.panel.game.save_replay()
    
    def on_apply_pgn(self, evt):
        pgn_string = wx.GetTextFromUser("Please insert the PGN of the turn you "
                                        "would like to apply", "Insert PGN")
        try:
            turn = from_pgn(pgn_string)
        except InvalidPGN:
            wx.MessageBox("Invalid PGN string provided.")
        else:
            try:
                self.panel.game.apply_own_turn(turn)
            except SquareNotEmpty:
                wx.MessageBox("The square you are trying to set your stone on "
                              "is not empty.")
    
    def on_undo(self, evt):
        self.panel.game.undo()
    
    def on_create_acc(self, evt):
        run_wizard(self, self.panel.conn)
    
    def on_close_game(self, evt):
        self.panel.conn.close_game()
    
    def on_bug_tracker(self, evt):
        browser_open(__bugs__)
    
    def on_open_game(self, evt):
        new_game_name = NewGameDialog(self, "Enter name of the game", 
                                            "Require name")
        if new_game_name.ShowModal() == wx.ID_OK:
            log.debug(new_game_name.game_name.Value)
            self.panel.conn.host_game(new_game_name.game_name.Value, 
                                     int(new_game_name.game_ranked.Value))

    def on_about(self, evt):
        config = get_conf_obj('client')
        
        gpl = open(join(script_path, "..", '..', '..', "COPYING")).read()
        info = wx.AboutDialogInfo()
        info.Name = "pyPentago"
        info.Version = __version__
        info.Copyright = __copyright__
        info.Description = wordwrap(__description__, 
                                    350, wx.ClientDC(self))
        info.WebSite = (__url__, 
                        "pyPentago home page")
        info.Developers = __authors__
        info.Artists = __artists__
        info.License = wordwrap(gpl, 500, wx.ClientDC(self))
        wx.AboutBox(info)
    
    def on_menu_exit(self, evt):
        # via wx.EVT_CLOSE event, also triggers exit dialog
        sys.exit(0)

    #def onCloseWindow(self, evt):
        ## dialog to verify exit (including menuExit)
        #dlg = wx.MessageDialog(self, "Want to exit?", "Exit", wx.YES_NO | 
        #wx.ICON_QUESTION)
        #if dlg.ShowModal() == wx.ID_YES:
            #self.Destroy() # frame
        #dlg.Destroy()
        #self.panel.Destroy()
        #self.Destroy()
        #sys.exit


def main(server="127.0.0.1", port=26500):
    log.info("Started pyPentago")
    from twisted.internet import wxreactor
    wxreactor.install()
    log.info("Initialized wxreactor")
    app = wx.PySimpleApp()
    frame = MainFrame(server, port)
    frame.Show()
    
    log.info("Started wxApp")
    from twisted.internet import reactor
    reactor.registerWxApp(app)
    reactor.run()
    app.MainLoop()
