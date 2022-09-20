import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from pubsub import pub

from app_settings import ApplicationSettings
from scope_mgr import TelescopeManager
from scope_status import TelescopeStatus
from scope_parameters import TelescopeParameters
from exception_formatter import ExceptionFormatter

from scope_nudge_view import TelescopeNudgeView
from scope_direct_slew_view import TelescopeDirectSlewView
from scope_tracking_rates_view import TelescopeTrackingRatesView
from scope_capabilities_view import TelescopeCapabilitiesView
from scope_parameters_view import TelescopeParametersView

from chooser import AlpacaDevice, Chooser


class TelescopeView:
    """
    This class manages the top-level telescope view which contains the
    Connect/Disconnect and Select buttons, as well as the tab widget
    that contains both the Motion, Direct Slew, Tracking Rates,
    Capabilities, and Static Properties views.
    """

    def __init__(self, parentFrame):
        # instance initializer

        self._parent = parentFrame
        self._isConnected = False
        self._mgr = TelescopeManager()
        self._status = TelescopeStatus()
        self._connectButtonText = tk.StringVar(master=None)
        self._connectButtonText.set("Connect Telescope")
        self._telescopeIdDisplay = tk.StringVar(master=None)

        # load the application settings and get the name of the
        # default telescope driver

        self._settings = ApplicationSettings.GetInstance()
        self._settings.InitFromSettingsFile()
        name = self._settings.TelescopeDriverName

        if len(name) != 0:
            name = f"({name})"
        self._telescopeIdDisplay.set(name)

        # initialize the parameters object

        self._parms = TelescopeParameters()

        self._CreateWidgets()

        # Start of Public Properties and Methods

    @property
    def IsConnected(self):
        return self._isConnected

    @IsConnected.setter
    def set_IsConnected(self, value):
        self._isConnected = value

    def ConnectTelescope(self):
        """
        Connect to the telescope
        """
        # subscribe to parameters updates

        pub.subscribe(self._ParmsListener, "TelescopeParametersUpdate")

        # send a message to the main view to select the hourglass cursor
        # in case the connect operation takes significant time.

        pub.sendMessage("change_cursor", wait=True)

        # do the connect

        success = self._mgr.Connect(
            self._settings.TelescopeAddress,
            self._settings.TelescopeDeviceNumber,
            self._settings.TelescopeProtocol,
        )

        # connect is complete, change back to the arrow cursor

        pub.sendMessage("change_cursor", wait=False)

        # report any connection error that we caught

        if not success:
            msg = self._mgr.ConnectionError + " Details follow:\r\n\r\n"
            xcp = self._mgr.ConnectException
            self._ShowExceptionError("Telescope Connection Error", msg, xcp)

            return False

        self._telescopeSelect_btn.config(state=tk.DISABLED)
        self._isConnected = True

        return True

    def DisconnectTelescope(self):
        # disconnect from the telescope and send a disconnect message to
        # subscribers

        try:
            self._mgr.Disconnect()
        except Exception as e:
            msg = "Unable to disconnect from the telescope. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError("Telescope Disconnection Error", msg, e)

            return

        self._telescopeSelect_btn.config(state=tk.NORMAL)
        self._isConnected = False

        name = self._settings.TelescopeDriverName

        if len(name) > 0:
            name = "(" + name + ")"

        self._telescopeIdDisplay.set(name)
        pub.sendMessage("ScopeDisconnect")

    # End of Public Properties and Methods

    # Start of Private Properties and Methods

    def _CreateWidgets(self):
        # add controls to the Telescope tab page

        # first add the Connect/Select button widgets to row 0

        row0Frame = tk.Frame(self._parent)
        row0Frame.rowconfigure(0)
        row0Frame.rowconfigure(1)
        row0Frame.columnconfigure(0, weight=1)

        btn = ttk.Button(row0Frame, textvariable=self._connectButtonText, width=20)
        state = tk.NORMAL
        if self._settings.TelescopeAddress == "":
            state = tk.DISABLED
        btn.config(command=self._OnConnectButtonClick, state=state)
        btn.grid(row=0, column=0, padx=4, pady=4, sticky="NW")
        self._telescopeConnect_btn = btn

        self._telescopeSelect_btn = ttk.Button(
            row0Frame, text="Select", command=self._OnSelectButtonClick
        )
        self._telescopeSelect_btn.grid(row=0, column=1, padx=6, pady=4, sticky="NW")

        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")
        lbl = ttk.Label(
            row0Frame, textvariable=self._telescopeIdDisplay, style="ValueText.TLabel"
        )
        lbl.grid(row=1, column=0, columnspan=2, padx=4, sticky="W")

        # second add the tab control to row 1
        row1Frame = tk.Frame(self._parent)

        scopeNotebook = ttk.Notebook(row1Frame)
        scopeNotebook.pack(expand=True, side=tk.TOP, pady=4)
        scopeNotebook.bind("<<NotebookTabChanged>>", self._OnTabChange)

        height = self._settings.WindowHeight
        width = self._settings.WindowHeight

        nudgeTab = ttk.Frame(scopeNotebook, height=height, width=width)
        directTab = ttk.Frame(scopeNotebook, height=height, width=width)
        ratesTab = ttk.Frame(scopeNotebook, height=height, width=width)
        capabilitiesTab = ttk.Frame(scopeNotebook, height=height, width=width)
        parametersTab = ttk.Frame(scopeNotebook, height=height, width=width)

        # create the views and add them to their tabs

        self._nudgeView = TelescopeNudgeView(nudgeTab, self._mgr)
        self._directSlewView = TelescopeDirectSlewView(directTab, self._mgr)
        self._trackingRatesView = TelescopeTrackingRatesView(ratesTab, self._mgr)
        self._capsView = TelescopeCapabilitiesView(capabilitiesTab)
        self._parmsView = TelescopeParametersView(parametersTab)

        # add the tab pages to the Telescope Notebook

        scopeNotebook.add(nudgeTab, text="Motion")
        scopeNotebook.add(directTab, text="Direct Slew")
        scopeNotebook.add(ratesTab, text="Tracking Rates")
        scopeNotebook.add(capabilitiesTab, text="Capabilities")
        scopeNotebook.add(parametersTab, text="Static Properties")

        row0Frame.grid(row=0, column=0, sticky="NW")
        row1Frame.grid(row=1, column=0)

    def _ParmsListener(self, parms):
        # callback to receive fresh parameters updates

        self._parms = parms
        name = self._parms.Name
        self._telescopeIdDisplay.set("(" + name + ")")
        # self._settings.TelescopeDriverName = name
        # self._settings.SaveSettings()

    def _OnConnectButtonClick(self):
        # click handler for the Connect/Disconnect button

        newText = ""

        if not self.IsConnected:
            self.ConnectTelescope()
            newText = "Disconnect Telescope"
        else:
            self.DisconnectTelescope()
            newText = "Connect Telescope"

        self._connectButtonText.set(newText)

    def _OnSelectButtonClick(self):
        # click handler for the Select button

        # pass in the parent of the view's parent to the chooser
        # to support centering the chooser on the main window

        chooser = Chooser(self._parent, "Telescope")
        device = chooser.Choose()

        if device is None:
            return

        self._selectedDevice = device
        self._telescopeIdDisplay.set(f"({device.Name})")
        self._telescopeConnect_btn.config(state=tk.NORMAL)

        # Update the settings with the selected device and save them

        self._settings.SetDeviceConfiguration(
            "telescope",
            device.Name,
            device.Address,
            device.DeviceNumber,
            device.Protocol,
        )

        self._settings.SaveSettings()

    def _OnTabChange(self, event):
        # handler for detecting changes to the selected tab page

        tab = event.widget.tab("current")["text"]

        # if the Direct Slew page was activated, send a message to its view
        # so that it can initialize the offset values.

        if tab == "Direct Slew":
            self._mgr.ImmediateStatusUpdate()
            pub.sendMessage("DirectSlewActivated")

    def _ShowExceptionError(self, title, message, xcp):
        msg = message
        formatter = ExceptionFormatter.GetInstance()
        msg += formatter.Format(xcp)
        root = self._parent
        messagebox.showerror(title, msg, parent=root)

    # End of Private Properties and Methods
