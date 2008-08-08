import wx


def set_pythonpath():
    # Set the PYTHONPATH
    from os.path import join, dirname, abspath
    import sys
    
    script_path = abspath(dirname(__file__))
    sys.path.append(abspath(join(script_path, "..", "..")))
    # End of setting the PYTHONPATH
if __name__ == "__main__":
    set_pythonpath()

from pypentago import IMGPATH
from os.path import join
########################################################################
class DisplayPlayerPanel(wx.Panel):
    """ Display Player information """

    #----------------------------------------------------------------------
    def __init__(self, parent, player):
        wx.Panel.__init__(self, parent)
        
        user_bitmap = wx.ArtProvider_GetBitmap(wx.ART_MISSING_IMAGE)
        self.user_image = wx.StaticBitmap(self, -1, user_bitmap)
        font = wx.Font(24, wx.FONTFAMILY_ROMAN, wx.FONTSTYLE_NORMAL, 
                       wx.FONTWEIGHT_BOLD)
        self.user_name = wx.StaticText(self, -1, player.login)
        self.user_name.SetFont(font)        
        
        self.profile = wx.TextCtrl(self, -1, player.profile, 
                                   style=wx.TE_READONLY | wx.TE_MULTILINE)
        items = {"Rating": player.current_rating, 
                 "Real Name": player.real_name}

                
        
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        top_sizer.Add(self.user_image)
        top_sizer.Add(self.user_name, flag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)

        sizer.Add(top_sizer, flag=wx.EXPAND)
        
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        item_sizer = wx.BoxSizer(wx.VERTICAL)
        for key, value in items.items():
            item_sizer.Add(wx.StaticText(self, -1, "%s: %s" % (key, value)))
        bottom_sizer.Add(item_sizer)
        
        bottom_sizer.Add(self.profile, 1, wx.EXPAND)
        sizer.Add(bottom_sizer, 1, wx.EXPAND)
        
        self.Sizer = sizer
        
        
        self.Fit()

class DisplayPlayerFrame(wx.Frame):
    """"""
    def __init__(self, player):
        wx.Frame.__init__(self, None,  -1, "pyPentago user information", 
                          size=(760, 810))
        self.panel = DisplayPlayerPanel(self, player)
        self.Fit()
        #self.make_menu()
        
def main():
    """ Function that is run when the file is executed on its own """
    app = wx.PySimpleApp()
    main_frame = DisplayPlayerFrame(None)
    main_frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    main()