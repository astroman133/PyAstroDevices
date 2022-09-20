import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from pubsub import pub

from app_settings import ApplicationSettings
from focuser_mgr import FocuserManager
from focuser_status import FocuserStatus
from focuser_parameters import FocuserParameters
from exception_formatter import ExceptionFormatter

from focuser_control_view import FocuserControlView
from focuser_parameters_view import FocuserParametersView

from chooser import AlpacaDevice, Chooser


class FocuserView:
    """
    This class manages the top-level focuser view which contains the
    Connect/Disconnect and Select buttons, as well as the tab widget
    that contains both the Control and Static Properties views.
    """

    def __init__(self, parentFrame):
        # the instance initializer

        self._parent = parentFrame
        self._isConnected = False
        self._mgr = FocuserManager()
        self._parms = FocuserParameters()
        self._status = FocuserStatus()
        self._connectButtonText = tk.StringVar(master=None)
        self._connectButtonText.set("Connect Focuser")
        self._focuserIdDisplay = tk.StringVar(master=None)

        self._settings = ApplicationSettings.GetInstance()
        self._settings.InitFromSettingsFile()
        name = self._settings.FocuserDriverName

        if len(name) > 0:
            name = f"({name})"

        self._focuserIdDisplay.set(name)

        self._CreateWidgets()

    # Start of Public Properties and Methods

    @property
    def IsConnected(self):
        return self._isConnected

    @IsConnected.setter
    def set_IsConnected(self, value):
        self._isConnected = value

    # End of Public Properties and Methods

    # Start of Private Properties and Methods

    def _ConnectFocuser(self):
        # call into the focuser manager to connect the focuser and begin
        # polling for status updates.

        # subscribe to get parameter updates

        pub.subscribe(self._ParmsListener, "FocuserParameterUpdate")

        # enable the wait cursor in case connection takes some time

        pub.sendMessage("change_cursor", wait=True)

        # connect the driver to the device

        success = self._mgr.Connect(
            self._settings.FocuserAddress,
            self._settings.FocuserDeviceNumber,
            self._settings.FocuserProtocol,
        )

        # go back to the arrow cursor

        pub.sendMessage("change_cursor", wait=False)

        # report any failure to the user

        if not success:
            msg = self._mgr.ConnectionError + " Details follow:\r\n\r\n"
            xcp = self._mgr.ConnectionException
            self._ShowExceptionError("Focuser Connection Error", msg, xcp)

            return False

        # set the isConnected variable and return success

        self._focuserSelect_btn.config(state=tk.DISABLED)
        self._isConnected = True

        return True

    def _DisconnectFocuser(self):
        # Disconnect from the focuser

        try:
            self._mgr.Disconnect()
        except Exception as e:
            msg = "Unable to disconnect from the focuser. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError("Telescope Disconnection Error", msg, e)

            return

        self._focuserSelect_btn.config(state=tk.NORMAL)
        self._isConnected = False

        # let the child views know that we have disconnected

        pub.sendMessage("FocuserDisconnect")

    def _CreateWidgets(self):
        # add controls to the Focuser tab page
        # create a frame with a grid 2 rows and one column

        row0Frame = tk.Frame(self._parent)
        row0Frame.rowconfigure(0)
        row0Frame.rowconfigure(1)
        row0Frame.columnconfigure(0, weight=1)

        # first add the Connect/Select button widgets to row 0

        self._focuserConnect_btn = ttk.Button(
            row0Frame, textvariable=self._connectButtonText, width=20
        )
        state = tk.NORMAL
        if self._settings.FocuserAddress == "":
            state = tk.DISABLED
        self._focuserConnect_btn.config(command=self._OnConnectButtonClick, state=state)
        self._focuserConnect_btn.grid(row=0, column=0, padx=4, pady=4)

        self._focuserSelect_btn = ttk.Button(
            row0Frame, text="Select", command=self._OnSelectButtonClick
        )
        self._focuserSelect_btn.grid(row=0, column=1, padx=6, pady=4, sticky="NW")

        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")
        focuserId_lbl = ttk.Label(
            row0Frame, textvariable=self._focuserIdDisplay, style="ValueText.TLabel"
        )
        focuserId_lbl.grid(row=1, column=0, columnspan=2, padx=4, sticky="W")

        # second add the tab control to row 1

        row1Frame = tk.Frame(self._parent)
        row1Frame.grid_rowconfigure(0, weight=1)
        row1Frame.grid_columnconfigure(0, weight=1)

        focusNotebook = ttk.Notebook(row1Frame)
        focusNotebook.pack(expand=True, side=tk.TOP, pady=4)

        height = self._settings.WindowHeight - 20
        width = self._settings.WindowHeight - 20

        controlTab = ttk.Frame(focusNotebook)
        controlTab.grid_rowconfigure(0, weight=1)
        controlTab.grid_columnconfigure(0, weight=1)

        parametersTab = ttk.Frame(focusNotebook)

        self._controlView = FocuserControlView(controlTab, self._mgr)
        self._parmsview = FocuserParametersView(parametersTab)

        focusNotebook.add(controlTab, text="Control")
        focusNotebook.add(parametersTab, text="Static Properties")

        row0Frame.grid(row=0, column=0, sticky="w")
        row1Frame.grid(row=1, column=0)

    def _ParmsListener(self, parms):
        # callback to get parameters updates on connect and disconnect

        self._parms = parms
        name = self._parms.Name
        self._focuserIdDisplay.set(f"({name})")

    def _OnConnectButtonClick(self):
        # initiate connect or disconnect and update the button text
        newText = ""
        if not self._isConnected:
            self._ConnectFocuser()
            newText = "Disconnect Focuser"
        else:
            self._DisconnectFocuser()
            newText = "Connect Focuser"

        self._connectButtonText.set(newText)

    def _OnSelectButtonClick(self):
        # click handler for the Select button

        # lanch our Alpaca chooser

        chooser = Chooser(self._parent, "Focuser")
        device = chooser.Choose()

        if device is None:
            return

        # update our view with the selected device

        self._selectedDevice = device
        self._focuserIdDisplay.set(f"({device.Name})")
        self._focuserConnect_btn.config(state=tk.NORMAL)

        # Update the settings with the selected device and save them

        self._settings.SetDeviceConfiguration(
            "focuser", device.Name, device.Address, device.DeviceNumber, device.Protocol
        )
        self._settings.SaveSettings()

    def _ShowExceptionError(self, title, message, xcp):
        msg = message
        formatter = ExceptionFormatter.GetInstance()
        msg += formatter.Format(xcp)
        root = self._parent
        messagebox.showerror(title, msg, parent=root)

    # Start of Private Properties and Methods
