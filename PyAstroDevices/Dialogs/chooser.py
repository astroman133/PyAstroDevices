import tkinter as tk
from tkinter import ttk
import threading as thread

from screeninfo import get_monitors
from pubsub import pub

from alpaca import management
from alpaca import discovery


class AlpacaDevice:
    """
    Class to contain the components of the REST address of an Alpaca device
    and to format those components into a partial URL
    """

    def __init__(self, name, deviceType, ipaddress, deviceNumber, protocol="http"):
        self._name = name
        self._deviceType = deviceType
        self._address = ipaddress
        self._deviceNumber = deviceNumber
        self._protocol = protocol

    @property
    def Name(self):
        return self._name

    def DeviceType(self):
        return self._deviceType

    @property
    def Address(self):
        return self._address

    @property
    def DeviceNumber(self):
        return self._deviceNumber

    @property
    def Protocol(self):
        return self._protocol

    def Format(self):
        """
        Format the class properties into a partial URL
        """
        formatted = self._name
        formatted += f"({self._address}/api/v1/{self._deviceType}/"
        formatted += f"{self._deviceNumber})"

        return formatted


class Chooser:
    """
    Class to provide the user with a list of Alpaca devices of a given
    device type.

    Positional arguments:
    parent     -- the parent tkinter Frame for the chooser dialog
    deviceType -- string containing the device type of interest
                                    , e.g. 'telescope'
    """

    def __init__(self, parent, deviceType):
        # perform initialization of the object instance

        self._parent = parent
        self._deviceType = deviceType
        self._selected = None
        self._dialogResult = None

    def Choose(self):
        """
        Allow the user to choose a discovered Alpaca device and return the
        selected device

        Returns -- the user-selected Alpaca device
        """
        # start with an empty list and perhaps get back the selected
        # device object

        selectedDevice = []
        result = self._ShowView(selectedDevice)

        device = None

        if result and len(selectedDevice) > 0:
            device = selectedDevice[0]

        return device

    def _ShowView(self, selectedDevice):
        # display the chooser dialog and populated it with any
        # discovered devices

        # subscribe to get the list of discovered devices when the discovery
        # thread completes

        pub.subscribe(self._DiscoveryListener, "DiscoveryList")

        # start the alpaca discovery process

        self._statusDisplay = tk.StringVar(master=None)
        self._statusDisplay.set("Active")

        t1 = thread.Thread(target=self._GetAlpacaDevicesTask)
        t1.start()

        # calculate a preliminary position for the dialog to be positioned over
        # the parent window. Below  we will adjust the position to keep the dialog
        # fully on the user's screen.

        viewWidth = 420
        viewHeight = 150
        rootx = self._parent.winfo_rootx()
        rooty = self._parent.winfo_rooty()
        viewX = int(rootx + (self._parent.winfo_width() - viewWidth) / 2)
        viewY = int(rooty + (self._parent.winfo_height() - viewHeight) / 2)

        # keep the position of the dialog completely on the screen

        monitors = get_monitors()

        screenWidth = self._GetMonitorsTotalWidth(monitors)
        screenHeight = self._GetMonitorsTotalHeight(monitors)

        if viewX < 0:
            viewX = 0

        if viewY < 0:
            viewY = 0

        if viewX + viewWidth > screenWidth:
            adjust = viewX + viewWidth - screenWidth
            viewX -= adjust

        if viewY + viewHeight > screenHeight:
            adjust = viewY + viewHeight - screenHeight
            viewY -= adjust

        # use the final values to position and size the dialog

        geometry = f"{viewWidth}x{viewHeight}+{viewX}+{viewY}"

        # create, initialize and show the dialog.

        self._dlg = tk.Toplevel(bd=1, relief="solid")
        self._dlg.resizable(False, False)

        self._dlg.attributes("-toolwindow", 1)
        self._dlg.title(f"{self._deviceType} Selector Dialog")
        self._dlg.geometry(geometry)
        self._dlg.wm_transient(self._parent)
        # configure the Close [x] button to do nothing
        self._dlg.protocol("WM_DELETE_WINDOW", self._DisableClose)

        self._dlg.grid_columnconfigure(0, weight=1)
        self._dlg.grid_rowconfigure(0)
        self._dlg.grid_rowconfigure(1)
        self._dlg.grid_rowconfigure(2)
        self._dlg.grid_rowconfigure(3)
        self._dlg.grid_rowconfigure(4)

        stsFrame = ttk.Frame(self._dlg)

        ttk.Label(stsFrame, text="Alpaca Discovery:").pack(side=tk.LEFT)

        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")
        lbl = ttk.Label(
            stsFrame,
            textvariable=self._statusDisplay,
            style="ValueText.TLabel",
            padding=(4, 0),
        )
        lbl.pack(side=tk.LEFT)

        stsFrame.grid(row=0, padx=6, pady=6, sticky="e")

        text = self._deviceType.lower()
        labelText = f"Select the type of {text} that you want to use."
        introLbl = ttk.Label(self._dlg, text=labelText)
        introLbl.grid(row=1, padx=6, pady=6, sticky="w")

        self._driverCbx = ttk.Combobox(self._dlg, width=60)
        self._driverCbx.grid(row=2, padx=4, pady=4, sticky="w")

        sepFrame = ttk.Frame(self._dlg)
        canvas = tk.Canvas(sepFrame, height=8, width=500)
        canvas.create_line(0, 6, 400, 6)
        canvas.pack()
        sepFrame.grid(row=3, sticky="ew")

        btnFrame = ttk.Frame(self._dlg)
        btnFrame.grid(row=4, padx=0, pady=0, sticky="e")

        width = 10
        self._okBtn = ttk.Button(
            btnFrame,
            text="OK",
            width=width,
            state="disabled",
            command=lambda: self._Result("ok"),
        )
        self._okBtn.grid(row=0, column=0, padx=6, pady=6)
        self._cancelBtn = ttk.Button(
            btnFrame,
            text="Cancel",
            width=width,
            state="disabled",
            command=lambda: self._Result("cancel"),
        )
        self._cancelBtn.grid(row=0, column=1, padx=6, pady=6)

        # initially show the dialog with the hourglass cursor,
        # until discovery completes

        self._dlg.focus()
        self._dlg.config(cursor="watch")
        self._dlg.update()

        # wait here until the dialog window has been closed

        self._dlg.wait_window(self._dlg)

        # extract and return the seleted device

        if self._selectedIndex > -1:
            selectedDevice.append(self._discoveredDevices[self._selectedIndex])

        # return True if the user selected a device and clicked OK,
        # otherwise return False

        return self.DialogResult

    def _GetMonitorsTotalWidth(self, monitors):
        # Find the monitor that starts farthest right
        # then add its width to its start position
        # to get the total width of all monitors.

        width = 0
        mmax = 0
        im = -1

        for i in range(len(monitors)):
            if monitors[i].x > mmax:
                im = i
                mmax = monitors[i].x

        width = mmax + monitors[im].width

        return width

    def _GetMonitorsTotalHeight(self, monitors):
        # Find the monitor that starts farthest down
        # then add its height to its start position
        # to get the total height of all monitors.

        height = 0
        mmax = 0
        im = -1

        for i in range(len(monitors)):
            if monitors[i].y > mmax:
                im = i
                mmax = monitors[i].y

        height = mmax + monitors[im].height

        return height

    def _DisableClose(self):
        # this empty method deactivates the close button at the end of the
        # title bar
        pass

    def _Result(self, option):
        # get whether the OK or Cancel button was used to exit the dialog
        # also get the index of the selected device.

        rslt = False
        ndx = -1

        if option == "ok":
            ndx = self._driverCbx.current()
            rslt = True

        # extract what we need from the dialog and then destroy it

        self.DialogResult = rslt
        self._selectedIndex = ndx

        self._dlg.destroy()

    def _GetAlpacaDevicesTask(self):
        # discover any Alpaca devices on the network and filter the list
        # to include only the requested device type

        deviceType = self._deviceType.lower()

        # create an empty dictionary to hold the list of devices to return

        devicesList = []

        # discover the Alpaca servers on the LAN

        alpacaServers = discovery.search_ipv4(numquery=1)

        # iterate through the responding servers to get the devices from
        # each one

        for alpacaServer in alpacaServers:
            # get the list of devices from this alpaca server
            alpacaDevices = management.configureddevices(alpacaServer)

            # iterate through the devices to find those for
            # the device type of interest

            for alpacaDevice in alpacaDevices:
                if alpacaDevice["DeviceType"].lower() == deviceType:

                    # here we have a device that we want to return
                    # so add it to the list

                    # for now, default the protocol to 'http'
                    deviceObj = AlpacaDevice(
                        alpacaDevice["DeviceName"],
                        deviceType,
                        alpacaServer,
                        alpacaDevice["DeviceNumber"],
                    )

                    devicesList.append(deviceObj)

        # finally send the list of discovered devices to populate the
        # dropdown list in the dialog

        pub.sendMessage("DiscoveryList", devices=devicesList)

    def _DiscoveryListener(self, devices):
        # this method is called when discovery has completed.
        # the 'devices' argument has the list of discovered devices.

        self._discoveredDevices = devices

        # format each device for display in the combobox and add it to
        # a display list

        dispList = []

        if devices is not None and len(devices) > 0:
            for i in range(0, len(devices)):
                dispList.append(devices[i].Format())

        self._driverCbx["values"] = dispList

        # select the first list item and update the status

        if len(dispList) > 0:
            self._driverCbx.current(0)
            self._statusDisplay.set("Finished")
        else:
            self._statusDisplay.set("Failed")

        # enable the OK and Cancel buttons

        self._okBtn.config(state="normal")
        self._cancelBtn.config(state="normal")

        # restore the arrow cursor

        self._dlg.config(cursor="")
        self._dlg.update()
