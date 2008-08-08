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

import wx
import wx.gizmos as gizmos

from pypentago import actions


class ListGames(wx.Panel, actions.ActionHandler):
    _decorators = []
    ID_HOST = 1
    ID_RANK = 2
    ID_GAMEID = 3
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        actions.ActionHandler.__init__(self)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = gizmos.TreeListCtrl(self, -1, style=wx.TR_DEFAULT_STYLE | 
                                        wx.TR_FULL_ROW_HIGHLIGHT)

        self.games = []
        self.parent = parent

        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.fldridx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,
                                                           wx.ART_OTHER, isz))
        self.fldropenidx = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, 
                                                           wx.ART_OTHER, isz))
        self.fileidx     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, 
                                                           wx.ART_OTHER, isz))
        self.tree.SetImageList(il)
        
        self.il = il

        # create some columns
        self.tree.AddColumn("Game")
        self.tree.AddColumn("Host")
        self.tree.AddColumn("Ranking")
        self.tree.AddColumn("Id")
        self.tree.SetMainColumn(0) # the one with the tree in it...
        self.tree.SetColumnWidth(0, 175)


        self.initItems()

        self.tree.Expand(self.root)
        

        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
    def joinGame(self, evt):
        """ Join game with the ID self.right_click_game_id """
        game_id = self.right_click_game_id
        if game_id:
            game_id = int(game_id)
            for game in self.games:
                if int(game.id) == int(game_id):
                    game.join()

    def showProfile(self, login):
        self.parent.conn.get_player(self.right_click_username)
    @actions.register_method('gamelist', _decorators)
    def refreshGames(self, games):
        self.tree.DeleteAllItems()
        self.games = []
        self.initItems()
        self.addGames(games)
    def addGames(self, games):
        for game in games:
            self.addGame(game)
    def addGame(self, game):
        if int(game.ranked):
            self.addRankedGame(game)
        else:
            self.addCasualGame(game)
        self.games.append(game)
        self.tree.Expand(self.root)
    def addGameTo(self, game, to):
        child = self.tree.AppendItem(to, game.name)
        self.tree.SetItemText(child, game.player, self.ID_HOST)
        self.tree.SetItemText(child, game.score, self.ID_RANK)
        self.tree.SetItemText(child, game.id, self.ID_GAMEID)        
    def addRankedGame(self, game):
        self.addGameTo(game, self.ranked)
    def addCasualGame(self, game):
        self.addGameTo(game, self.casual)
    def initItems(self):
        self.root = self.tree.AddRoot("Games")        
        self.ranked = self.tree.AppendItem(self.root, "Ranked Games")
        self.casual = self.tree.AppendItem(self.root, "Casual Games")
        self.folderIcon([self.root, self.ranked, self.casual])
    def folderIcon(self, items):
        for item in items:
            self.tree.SetItemImage(item, self.fldridx, which = 
                                   wx.TreeItemIcon_Normal)
            self.tree.SetItemImage(item, self.fldropenidx, which = 
                                   wx.TreeItemIcon_Selected)        
    def OnActivate(self, evt):
        game_id = self.tree.GetItemText(evt.GetItem(), self.ID_GAMEID)
        if game_id:
            game_id = int(game_id)
            for game in self.games:
                if int(game.id) == int(game_id):
                    game.join()

    def OnRightUp(self, evt):
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        self.right_click_username = self.tree.GetItemText(item, self.ID_HOST)
        self.right_click_game_id = self.tree.GetItemText(item, self.ID_GAMEID)
        
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.Bind(wx.EVT_MENU, self.joinGame, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.showProfile, id=self.popupID2)
        if self.right_click_game_id:
            menu = wx.Menu()
            menu.Append(self.popupID1, "Join Game")
            menu.Append(self.popupID2, "Show hosts profile")
    
            self.PopupMenu(menu)
            menu.Destroy()


    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())

class ListGamesFrame(wx.Frame):
    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent)
        panel = ListGames(self)
        
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = ListGamesFrame(None)
    frame.Show()
    app.MainLoop()
