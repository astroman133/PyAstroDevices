import os
import locale

import tkinter as tk
from tkinter import FLAT, ttk
from tkinter import messagebox
from pubsub import pub

from app_settings import ApplicationSettings
from scope_view import TelescopeView
from focuser_view import FocuserView


class Application(tk.Frame):
    """
    This class manages the application top-level user interface for the
    PyAstroDevices GUI application.

    It uses a private SETTINGS_FILE environment variable to make the name
    of the JSON settings file, settings.json, available to the
    ApplicationSettings class.
    """

    def __init__(self, parent, settings):
        """
        Initializer method for the Application class

        Positional arguments:
        parent   -- the root tkinter instance
        settings -- instance of the ApplicationSettings object
        """

        tk.Frame.__init__(self, parent)
        self._parent = parent
        self._settings = settings
        pub.subscribe(self._ChangeCursorListener, "change_cursor")

        # define the shutdown handler

        parent.protocol("WM_DELETE_WINDOW", self._Shutdown)

        self._CreateWidgets()

    def _CreateWidgets(self):
        # create top level user interface

        # create the tab control

        devicesNotebook = ttk.Notebook(self)
        devicesNotebook.pack(expand=True)

        # add the telescope and focuser tab pages

        height = self._settings.WindowHeight
        width = self._settings.WindowWidth

        scopeTab = ttk.Frame(devicesNotebook, height=height, width=width)
        focuserTab = ttk.Frame(devicesNotebook, height=height, width=width)

        devicesNotebook.add(scopeTab, text="Telescope")
        devicesNotebook.add(focuserTab, text="Focuser")

        # add the device views to the tab pages

        self._scopeView = TelescopeView(scopeTab)
        self._focuserView = FocuserView(focuserTab)

    def _ChangeCursorListener(self, wait):
        # change the application cursor between the hourglass and the arrow

        cursor = ""

        if wait:
            cursor = "watch"

        self.config(cursor=cursor)
        self.update()

    def _Shutdown(self):
        # shut down the application in preparation for an orderly exit.

        # allow graceful disconnect before shutting down

        scopeConnected = self._scopeView.IsConnected
        focuserConnected = self._focuserView.IsConnected

        if scopeConnected or focuserConnected:
            msg = "You are currently connected to "

            if scopeConnected and focuserConnected:
                msg += "a telescope and a focuser"
            elif scopeConnected:
                msg += "a telescope"
            else:
                msg += "a focuser"

            msg += ".\r\n\r\nAre you sure that you want to disconnect and exit?"

            if messagebox.askokcancel("Okay to continue", msg):
                if scopeConnected:
                    self._scopeView.DisconnectTelescope()
                if focuserConnected:
                    # self._focuserView.DisconnectFocuser()
                    pass
            else:
                return

        # update the application settings with the current window size and
        # position

        settings = ApplicationSettings.GetInstance()
        settings.SetWindowSize(root.winfo_height(), root.winfo_width())
        settings.SetWindowPosition(root.winfo_x(), root.winfo_y())
        settings.SaveSettings()

        # destroy the main tk object to terminate the message loop

        root.destroy()


if __name__ == "__main__":
    """
    Main entry point to the application
    """
    # Initialize the current locale to the user's selection

    locale.setlocale(locale.LC_ALL, "")

    # create the root tkinter object instance

    root = tk.Tk()

    # add the name of our app settings file to the local environment

    os.environ["SETTINGS_FILE"] = "settings.json"

    # create a settings object and initialize it from any existing settings file

    settings = ApplicationSettings()
    settings.InitFromSettingsFile()

    # configure the main window

    root.resizable(False, False)
    root.config(bd="1", relief="solid")
    root.iconbitmap(default="./assets/telescope.ico")

    # TODO make sure that the position is on the screen

    root.geometry(settings.Geometry)
    root.title(settings.WindowTitle)

    # create the application instance

    app = Application(root, settings)
    app.pack(side="top", fill="both", expand=True)

    root.mainloop()
