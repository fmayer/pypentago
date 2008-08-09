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

import string
import logging

import wx
import wx.wizard as wiz

from os.path import dirname, join
from hashlib import sha1 as sha

from pypentago.client.interface.validators import ValidateEmail, ValidateName
from pypentago import actions

script_path = dirname(__file__)
imgpath = join(script_path, "..", "img")

TEXTCTRL_SIZE = (150, -1)
EMAILCTRL_SIZE = (250, -1)

#----------------------------------------------------------------------
def make_page_title(wizPg, title):
    sizer = wx.BoxSizer(wx.VERTICAL)
    wizPg.SetSizer(sizer)
    title = wx.StaticText(wizPg, -1, title)
    title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
    sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
    sizer.Add(wx.StaticLine(wizPg, -1), 0, wx.EXPAND|wx.ALL, 5)
    return sizer


#----------------------------------------------------------------------
class AvailabilityIcon(wx.StaticBitmap):
    def __init__(self, parent):
        wx.StaticBitmap.__init__(self, parent)
        self.imgpath = imgpath
        self.Debug()
        self.red = True
    
    def Debug(self):
        self.SetBitmap(wx.Bitmap(join(self.imgpath, "status_yellow.png")))
    
    def SetGreen(self):
        self.SetBitmap(wx.Bitmap(join(self.imgpath, "status_green.png")))
        self.red = False
    
    def SetRed(self):
        self.SetBitmap(wx.Bitmap(join(self.imgpath, "status_red.png")))
        self.red = True


#----------------------------------------------------------------------
class DummyMain(object):
    def GetValue(self):
        return False
    
    Value = value = property(GetValue)

#----------------------------------------------------------------------    
class TitledPage(wiz.PyWizardPage):
    def __init__(self, parent, title):
        wiz.PyWizardPage.__init__(self, parent)
        self.sizer = make_page_title(self, title)
        self.main = DummyMain()
    
    def AddContent(self, widget, flags=False):
        if not flags:
            self.sizer.Add(widget)
        else:
            self.sizer.Add(widget, flags)
    
    def GetValue(self):
        if hasattr(self.main, "Value"):
            return self.main.Value
        elif hasattr(self.main, "Label"):
            return self.main.Label
        else:
            raise TypeError("self.main must either have a Value or a Label "
                            "attribute")
    
    def SetValue(self, val):
        self.main.Value = val

    def GetNext(self):
        self.Parent.confirm.refresh()
        index = self.Parent.pages.index(self)
        if not index == len(self.Parent.pages)-1:
            #self.Parent.pages[index + 1].refresh()
            return self.Parent.pages[index + 1]
        
    def GetPrev(self):
        index = self.Parent.pages.index(self)
        if not index == 0:
            #self.Parent.pages[index - 1].refresh()
            return self.Parent.pages[index - 1]
    
    def refresh(self):
        pass
    
    value = property(GetValue, SetValue)


#----------------------------------------------------------------------    
class Introduction(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, "Introduction")
        self.confirm_name = False
        self.AddContent(
            wx.StaticText(self, -1,
                          "Welcome to the pyPentago account creation wizard.\n"
                          "It will assist you in creating an account "
                          "with the pyPentago server.\n"
                          "This will allow you to enjoy all the features "
                          "of pyPentago, such as ranked gaming"
                          )
        )
        
#----------------------------------------------------------------------
class UserName(TitledPage, actions.ActionHandler):
    _decorators = []
    def __init__(self, parent):
        TitledPage.__init__(self, parent, "User Name")
        actions.ActionHandler.__init__(self)
        
        self.SetName("User Name")
        self.confirm_name = "Name"
        self.AddContent(
            wx.StaticText(self, -1,
                          "Please enter your desired username.\n"
                          "You will not be able to change it later"
                          )
        )
        name_sizer = wx.BoxSizer()
        self.main = self.name_ctrl = wx.TextCtrl(self, -1,  
                                     size = TEXTCTRL_SIZE, 
                                     validator=ValidateName(self))
        self.avail = AvailabilityIcon(self)
        name_sizer.Add(self.name_ctrl, wx.ALIGN_CENTER_VERTICAL)
        name_sizer.Add(self.avail, wx.ALIGN_CENTER_VERTICAL)
        self.AddContent(name_sizer)
        self.name_ctrl.Bind(wx.EVT_TEXT, self.checkAvailability)
    
    def refresh(self):
        pass
    
    def checkAvailability(self, evt):
        text_ctrl = evt.GetEventObject()
        name = text_ctrl.Value
        self.Parent.conn.name_availability(name)
    
    @actions.register_method('name_available', _decorators)
    def nameAvail(self, state):
        if state:
            self.nameAvailable()
        else:
            self.nameUnAvailable()
    
    def nameAvailable(self, name=False):
        self.avail.SetGreen()
        self.available = True
    
    def nameUnAvailable(self, name=False):
        self.avail.SetRed()
        self.available = False


#----------------------------------------------------------------------
class Password(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, "Password")
        self.SetName("Password")
        self.confirm_name = "Passwd"
        self.AddContent(
            wx.StaticText(self, -1,
                          "Please enter your password.\n"
                          "Please note that it is case sensetive and that it "
                          "may not contain any non-standard characters"
                          )
        )
        self.main = self.passwd = wx.TextCtrl(self, -1,  
                                  style = wx.TE_PASSWORD, size = TEXTCTRL_SIZE)
        self.AddContent(self.passwd)
        self.passwd.Bind(wx.EVT_TEXT, self.onText)
    
    def onText(self, evt):
        pass
    
    def refresh(self):
        pass
    
#----------------------------------------------------------------------
class RealName(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, "Real Name")
        self.SetName("Real Name")
        self.confirm_name = "Real_Name" 
        self.AddContent(
            wx.StaticText(self, -1,
                          "Please enter your real name\n"
                          "This may also be a username you want to use.\n"
                          "You can change your real name later, other than your"
                          " username"
                          )
        )
        self.main = self.real_name = wx.TextCtrl(self, -1,   
                                                 size=TEXTCTRL_SIZE)
        self.AddContent(self.real_name)
        self.real_name.Bind(wx.EVT_TEXT, self.onText)
    
    def onText(self, evt):
        pass
    
    def refresh(self):
        pass 
    
#----------------------------------------------------------------------
class Email(TitledPage, actions.ActionHandler):
    _decorators = []
    def __init__(self, parent):
        TitledPage.__init__(self, parent, "Email Address")
        actions.ActionHandler.__init__(self)
        self.SetName("Email Address")
        self.confirm_name = "Email"
        self.AddContent(
            wx.StaticText(self, -1,
                          "Please enter your email address.\n"
                          "We need it to inform you of any available updates "
                          "or other important information.\n"
                          "We will never give your adress to anyone else.\n"
                          "It will be used to recover your password "
                          "if it is lost"
                          )
        )
        name_sizer = wx.BoxSizer()
        self.main = self.email = wx.TextCtrl(self, -1, size = EMAILCTRL_SIZE, 
                                             validator=ValidateEmail())
        self.avail = AvailabilityIcon(self)
        name_sizer.Add(self.email, wx.ALIGN_CENTER_VERTICAL)
        name_sizer.Add(self.avail, wx.ALIGN_CENTER_VERTICAL)
        self.AddContent(name_sizer)
        self.email.Bind(wx.EVT_TEXT, self.checkAvailability)
    
    def checkAvailability(self, evt):
        text_ctrl = evt.GetEventObject()
        name = text_ctrl.Value
        self.Parent.conn.email_availability(name)
    
    @actions.register_method('email_available', _decorators)
    def emailAvail(self, state):
        if state:
            self.emailAvailable()
        else:
            self.emailUnAvailable()
    
    def emailAvailable(self, name=False):
        self.avail.SetGreen()
    
    def emailUnAvailable(self, name=False):
        self.avail.SetRed()
    
    def refresh(self):
        pass


#----------------------------------------------------------------------
class Profile(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, "Profile text")
        self.SetName("Profile text")
        self.confirm_name = "Profile"
        self.AddContent(
            wx.StaticText(self, -1,
                          "Please enter some optional information about "
                          "yourself that you wish to be publically viewable "
                          "in your profile"
                          )
        )
        self.main = self.profile = wx.TextCtrl(self, -1, 
                                               style = wx.TE_MULTILINE, 
                                               size=self.Parent.GetSize()) 

        self.AddContent(self.profile, wx.EXPAND | wx.ALIGN_CENTER)
    
    def refresh(self):
        pass
    
#----------------------------------------------------------------------
class Confirmation(TitledPage):
    def __init__(self, parent):
        TitledPage.__init__(self, parent, "Confirmation")
        self.main = wx.StaticText(self, -1)
        self.AddContent(self.main)
    
    def refresh(self):
        text = ""
        for page in self.Parent.pages:
            if not isinstance(page, Confirmation) and page.confirm_name:
                if page.confirm_name.lower() == 'passwd':
                    text+="%s %s\n" % (page.GetName(), "*"*len(page.value))
                else:
                    text+="%s %s\n" % (page.GetName(), page.value)
        self.main.Label = text


#----------------------------------------------------------------------
def run_wizard(parent=None, conn=None):
    user_wizard = wiz.Wizard(parent, -1, "User creation wizard")
    user_wizard.conn = conn
    conn.wizard = user_wizard
    pages = [Introduction(user_wizard), UserName(user_wizard), 
             Password(user_wizard),  Email(user_wizard), 
             RealName(user_wizard), 
             Profile(user_wizard), Confirmation(user_wizard)]
    user_wizard.confirm = pages[-1]
    user_wizard.user_name = pages[1]
    user_wizard.email = pages[3]
    user_wizard.pages = pages

    user_wizard.FitToPage(pages[0])
    wx.FindWindowById(wx.ID_FORWARD).Enable(True)
    if not user_wizard.RunWizard(pages[0]):
        return False
    results = {}
    for page in pages[:-1]:
        if page.value:
            results[page.confirm_name.lower()] = page.value
    user_wizard.conn.send("REGISTER",
                          (results['name'], 
                          sha(results['passwd']).hexdigest(), 
                          results['email'], 
                          results['profile'], 
                          results['real_name']))


if __name__ == "__main__":
    app = wx.PySimpleApp()
    run_wizard()

