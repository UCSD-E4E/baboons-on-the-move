import wx

from gui.baboon_tracker_thread import BaboonTrackerThread

PROGRESS_EVT_RESULT_ID = wx.NewId()
FINISHED_EVT_RESULT_ID = wx.NewId()


def PROGRESS_EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, PROGRESS_EVT_RESULT_ID, func)


def FINISHED_EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, FINISHED_EVT_RESULT_ID, func)


class ProgressEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(PROGRESS_EVT_RESULT_ID)
        self.data = data


class FinishedEvent(wx.PyEvent):
    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(FINISHED_EVT_RESULT_ID)


class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Baboon Tracker")

        self._make_menu()
        self._progress = None

        PROGRESS_EVT_RESULT(self, self._on_update_value)
        FINISHED_EVT_RESULT(self, self._on_finished)

    def _make_menu(self):
        file_menu = wx.Menu()
        open_item = file_menu.Append(wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self._on_open, open_item)
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self._on_exit, exit_item)

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")

        self.MenuBar = menu_bar

    def _on_open(self, _):
        file_dialog = wx.FileDialog(self, wildcard="Video Files (*.mp4)|*.mp4")
        result = file_dialog.ShowModal()

        if result == wx.ID_OK:
            thread = BaboonTrackerThread(
                file_dialog.Path, self._update_value_callback, self._finished_callback
            )
            thread.start()

            self._progress = wx.ProgressDialog(
                "Processing Video...",
                "Processing Video...",
                style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME,
                maximum=thread.get_frame_count(),
            )

    def _update_value_callback(self, value):
        wx.PostEvent(self, ProgressEvent(value))

    def _finished_callback(self):
        wx.PostEvent(self, FinishedEvent())

    def _on_update_value(self, event: ProgressEvent):
        self._progress.Update(event.data)

    def _on_finished(self, _):
        self._progress.Destroy()

    def _on_exit(self, _):
        self.Close()
