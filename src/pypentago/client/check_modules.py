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

def check_modules(modular=True):
    try:
        import twisted
        twisted = True
    except ImportError:
        twisted = False
    try:
        import wx
        if wx.VERSION >= (2, 8, 0, 0, ''):
            wxpy = True
        else:
            wxpy = "VERSION"
    except ImportError:
        wxpy = False
    output = ""
    if not twisted:
        output+="You need Twisted to run pyPentago\n"
    if wxpy:
        app = wx.PySimpleApp()
        if wxpy == "VERSION":
            output+="You need at least wxPython 2.8 to run pyPentago\n"
        if output:
            if modular:
                return (False, twisted, wxpy)
            else:
                wx.MessageBox(output, "Dependencies not met")
        else:
            if modular:
                return (True, twisted, wxpy)
            else:
                wx.MessageBox("You have all dependencies to run pyPentago")
    else:
        output+="You need wxPython to run pyPentago\n"
        return (False, twisted, wxpy)
        
if __name__ == "__main__":
    check_modules(False)