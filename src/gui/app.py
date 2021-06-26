import wx

from gui.main_frame import MainFrame


class BaboonTrackingApp:
    def run(self):
        app = wx.App()

        main_frame = MainFrame()
        main_frame.Show()

        app.MainLoop()
