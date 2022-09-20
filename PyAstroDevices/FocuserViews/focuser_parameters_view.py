import locale

import tkinter as tk
from tkinter import ttk
from pubsub import pub
from alpaca.focuser import *  # Multiple Classes including Enumerations

from focuser_parameters import FocuserParameters


class FocuserParametersView:
    """
    This class manages the display and interaction of the widgets on the
    Focuser Static Properties tab page
    """

    def __init__(self, parentFrame):
        # instance initializer

        self._parent = parentFrame

        # create the variables that are bound to the U/I

        self._absolute = tk.StringVar(master=None)
        self._description = tk.StringVar(master=None)
        self._driverInfo = tk.StringVar(master=None)
        self._driverVersion = tk.StringVar(master=None)
        self._interfaceVersion = tk.StringVar(master=None)
        self._maximumIncrement = tk.StringVar(master=None)
        self._maximumStep = tk.StringVar(master=None)
        self._stepSize = tk.StringVar(master=None)
        self._tempCompAvailable = tk.StringVar(master=None)

        self._CreateWidgets()

        # fill the parameters instance with default values and populate
        # the U/I

        parms = FocuserParameters()
        self._ParmsListener(parms)

        pub.subscribe(self._ParmsListener, "FocuserParametersUpdate")

    # Start of Public Properties and Methods

    # End of Public Properties and Methods

    # Start of Private Properties and Methods

    def _CreateWidgets(self):
        # create the widgets on the Focuser Parameters tab page

        # first create the main frame and divide it into two columns and
        # enough rows to hold all the parameters

        parmsFrame = tk.Frame(self._parent)

        for p in range(8):
            parmsFrame.grid_rowconfigure(p)

        parmsFrame.grid_columnconfigure(0)
        parmsFrame.grid_columnconfigure(1)

        # add the parameter labels to the grid

        ttk.Label(parmsFrame, text="Absolute:").grid(row=0, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Description:").grid(row=1, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Driver Info:").grid(row=2, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Driver Version:").grid(row=3, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Interface Version:").grid(
            row=4, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Maximum Increment:").grid(
            row=5, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Maximum Step:").grid(row=6, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Step Size (microns):").grid(
            row=7, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Temperature Compensation Available:").grid(
            row=8, column=0, sticky="E"
        )

        # add the value labels to the grid, styling the text in red
        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")

        ttk.Label(
            parmsFrame, textvariable=self._absolute, style="ValueText.TLabel"
        ).grid(row=0, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._description, style="ValueText.TLabel"
        ).grid(row=1, column=1, sticky="W")

        # add a 2x2 grid to contain a listbox to hold the DriverInfo string
        # as well as an additional row and column for the scrollbars.

        infoFrame = tk.Frame(parmsFrame)
        infoFrame.grid_rowconfigure(0)
        infoFrame.grid_rowconfigure(1)
        infoFrame.grid_columnconfigure(0)
        infoFrame.grid_columnconfigure(1)

        # create the listbox and scrollbars

        self._driverInfoList = tk.Listbox(
            infoFrame,
            listvariable=self._driverInfo,
            height=6,
            width=30,
            state=tk.DISABLED,
            disabledforeground="red",
        )
        self._driverInfoList.grid(row=0, column=0, sticky="ew")
        self._driverInfoHScroller = ttk.Scrollbar(
            infoFrame, orient="horizontal", command=self._driverInfoList.xview
        )
        self._driverInfoList["xscrollcommand"] = self._driverInfoHScroller.set
        self._driverInfoHScroller.grid(row=1, column=0, sticky="ew")
        self._driverInfoVScroller = ttk.Scrollbar(
            infoFrame, orient="vertical", command=self._driverInfoList.yview
        )
        self._driverInfoList["yscrollcommand"] = self._driverInfoVScroller.set
        self._driverInfoVScroller.grid(row=0, column=1, sticky="ns")

        infoFrame.grid(row=2, column=1, sticky="w")

        # add the remaining value labels

        ttk.Label(
            parmsFrame, textvariable=self._driverVersion, style="ValueText.TLabel"
        ).grid(row=3, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._interfaceVersion, style="ValueText.TLabel"
        ).grid(row=4, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._maximumIncrement, style="ValueText.TLabel"
        ).grid(row=5, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._maximumStep, style="ValueText.TLabel"
        ).grid(row=6, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._stepSize, style="ValueText.TLabel"
        ).grid(row=7, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._tempCompAvailable, style="ValueText.TLabel"
        ).grid(row=8, column=1, sticky="W")

        parmsFrame.pack(side=tk.TOP, anchor="nw", fill="x", pady=3)
        self._parent.pack()

    def _ParmsListener(self, parms):
        # callback to handle messages to update the parameter values

        self._parms = parms

        if not parms.IsConnected:
            bl = ""
            empty = ()
            self._absolute.set(bl)
            self._description.set(bl)
            self._driverInfo.set(empty)
            self._driverVersion.set(bl)
            self._interfaceVersion.set(bl)
            self._maximumIncrement.set(bl)
            self._maximumStep.set(bl)
            self._stepSize.set(bl)
            self._tempCompAvailable.set(bl)
        else:
            self._absolute.set(str(parms.Absolute))
            self._description.set(parms.Description)
            self._driverInfo.set(parms.DriverInfo)
            self._driverVersion.set(parms.DriverVersion)
            self._interfaceVersion.set(str(parms.InterfaceVersion))
            self._maximumIncrement.set(str(parms.MaxIncrement))
            self._maximumStep.set(str(parms.MaxStep))
            stepStr = locale.format_string("%.1f", parms.StepSize)
            self._stepSize.set(stepStr)
            self._tempCompAvailable.set(str(parms.TempCompAvailable))

    # End of Private Properties and Methods
