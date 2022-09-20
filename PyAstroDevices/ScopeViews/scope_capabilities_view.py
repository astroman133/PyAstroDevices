import locale

import tkinter as tk
from tkinter import ttk
from pubsub import pub

from scope_capabilities import TelescopeCapabilities


class TelescopeCapabilitiesView(object):
    """
    This class manages the display and interaction of the widgets on the
    Telescope Capabilities tab page
    """

    def __init__(self, parentFrame):
        # instance initializer

        self._parent = parentFrame

        # create the variables that are bound to the U/I

        self._canFindHome = tk.StringVar(master=None)
        self._canPark = tk.StringVar(master=None)
        self._canPulseGuide = tk.StringVar(master=None)
        self._canSetDeclinationRate = tk.StringVar(master=None)
        self._canSetGuideRates = tk.StringVar(master=None)
        self._canSetPark = tk.StringVar(master=None)
        self._canSetPierSide = tk.StringVar(master=None)
        self._canSetRightAscensionRate = tk.StringVar(master=None)
        self._canSetTracking = tk.StringVar(master=None)
        self._canSlew = tk.StringVar(master=None)
        self._canSlewAltAz = tk.StringVar(master=None)
        self._canSlewAltAzAsync = tk.StringVar(master=None)
        self._canSlewAsync = tk.StringVar(master=None)
        self._canSync = tk.StringVar(master=None)
        self._canSyncAltAz = tk.StringVar(master=None)
        self._canUnpark = tk.StringVar(master=None)
        self._canMovePrimaryAxis = tk.StringVar(master=None)
        self._canMoveSecondaryAxis = tk.StringVar(master=None)
        self._canMoveTertiaryAxis = tk.StringVar(master=None)

        self._CreateWidgets()

        # fill the capabilities instance with default values
        self._caps = TelescopeCapabilities()

        self._CapsListener(self._caps)

        # create the capabilities update listener

        pub.subscribe(self._CapsListener, "TelescopeCapabilitiesUpdate")

    # Start of Public Properties and Methods

    # End of Public Properties and Methods

    # Start of Private Properties and Methods

    def _CreateWidgets(self):
        # create the widgets on the Telescope Capabilities tab page

        # first create the left frame to hold the CanXXX variables
        # divide it into two columns and enough rows to hold all
        # the variables

        capsFrame = tk.Frame(self._parent)
        capsFrame.grid_rowconfigure(0)
        capsFrame.grid_columnconfigure(0)
        capsFrame.grid_columnconfigure(1)

        canValuesFrame = tk.Frame(capsFrame)
        canValuesFrame.grid(row=0, column=0, sticky="NW")

        for r in range(17):
            canValuesFrame.grid_rowconfigure(r)

        for c in range(1):
            canValuesFrame.grid_columnconfigure(c)

        # create the labels in column 0 of the left frame

        ttk.Label(canValuesFrame, text="Can Find Home:").grid(
            row=0, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Park:").grid(row=1, column=0, sticky="E")
        ttk.Label(canValuesFrame, text="Can Pulse Guide:").grid(
            row=2, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Set Declination Rate:").grid(
            row=3, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Set Guide Rates:").grid(
            row=4, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Set Park:").grid(
            row=5, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Set Pier Side:").grid(
            row=6, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Set Right Ascension Rate:").grid(
            row=7, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Set Tracking:").grid(
            row=8, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Slew:").grid(row=9, column=0, sticky="E")
        ttk.Label(canValuesFrame, text="Can Slew Alt Az:").grid(
            row=10, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Slew Alt Az Async:").grid(
            row=11, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Slew Async:").grid(
            row=12, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Sync:").grid(row=13, column=0, sticky="E")
        ttk.Label(canValuesFrame, text="Can Sync Alt Az:").grid(
            row=14, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Unpark:").grid(row=15, column=0, sticky="E")
        ttk.Label(canValuesFrame, text="Can Move Primary Axis:").grid(
            row=16, column=0, sticky="E"
        )
        ttk.Label(canValuesFrame, text="Can Move Secondary Axis:").grid(
            row=17, column=0, sticky="E"
        )

        # put the value labels in column 1 of the left frame.
        # give them a red foreground color and bind them
        # to the Tk variables that we declared in the initializer

        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")
        ttk.Label(
            canValuesFrame, textvariable=self._canFindHome, style="ValueText.TLabel"
        ).grid(row=0, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canPark, style="ValueText.TLabel"
        ).grid(row=1, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canPulseGuide, style="ValueText.TLabel"
        ).grid(row=2, column=1, sticky="W")
        ttk.Label(
            canValuesFrame,
            textvariable=self._canSetDeclinationRate,
            style="ValueText.TLabel",
        ).grid(row=3, column=1, sticky="W")
        ttk.Label(
            canValuesFrame,
            textvariable=self._canSetGuideRates,
            style="ValueText.TLabel",
        ).grid(row=4, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canSetPark, style="ValueText.TLabel"
        ).grid(row=5, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canSetPierSide, style="ValueText.TLabel"
        ).grid(row=6, column=1, sticky="W")
        ttk.Label(
            canValuesFrame,
            textvariable=self._canSetRightAscensionRate,
            style="ValueText.TLabel",
        ).grid(row=7, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canSetTracking, style="ValueText.TLabel"
        ).grid(row=8, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canSlew, style="ValueText.TLabel"
        ).grid(row=9, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canSlewAltAz, style="ValueText.TLabel"
        ).grid(row=10, column=1, sticky="W")
        ttk.Label(
            canValuesFrame,
            textvariable=self._canSlewAltAzAsync,
            style="ValueText.TLabel",
        ).grid(row=11, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canSlewAsync, style="ValueText.TLabel"
        ).grid(row=12, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canSync, style="ValueText.TLabel"
        ).grid(row=13, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canSyncAltAz, style="ValueText.TLabel"
        ).grid(row=14, column=1, sticky="W")
        ttk.Label(
            canValuesFrame, textvariable=self._canUnpark, style="ValueText.TLabel"
        ).grid(row=15, column=1, sticky="W")
        ttk.Label(
            canValuesFrame,
            textvariable=self._canMovePrimaryAxis,
            style="ValueText.TLabel",
        ).grid(row=16, column=1, sticky="W")
        ttk.Label(
            canValuesFrame,
            textvariable=self._canMoveSecondaryAxis,
            style="ValueText.TLabel",
        ).grid(row=17, column=1, sticky="W")

        # now create the right frame to hold the axis rates

        ratesFrame = tk.Frame(capsFrame)
        ratesFrame.grid(row=0, column=1, sticky="NW", padx=(10, 0))

        ratesFrame.grid_rowconfigure(0)
        ratesFrame.grid_rowconfigure(1)
        ratesFrame.grid_columnconfigure(0)

        self._primaryAxisFrame = tk.LabelFrame(ratesFrame, text="Primary Axis Rates")
        self._primaryAxisFrame.grid(row=0, column=0, sticky="W")

        self._secondaryAxisFrame = tk.LabelFrame(
            ratesFrame, text="Secondary Axis Rates"
        )
        self._secondaryAxisFrame.grid(row=1, column=0, sticky="W", pady=10)

        capsFrame.pack(pady=3, side=tk.TOP, anchor="nw", fill="x")
        self._parent.pack()

    def _CapsListener(self, caps):
        # callback to handle messages with fresh capabilities values
        # this is called 1) at startup, 2) after connection with the driver,
        # and 3) on disconnect from the driver

        self._caps = caps

        if not caps.IsConnected:
            # we are not connected, so default all the values

            bl = ""
            self._canFindHome.set(bl)
            self._canPark.set(bl)
            self._canPulseGuide.set(bl)
            self._canSetDeclinationRate.set(bl)
            self._canSetGuideRates.set(bl)
            self._canSetPark.set(bl)
            self._canSetPierSide.set(bl)
            self._canSetRightAscensionRate.set(bl)
            self._canSetTracking.set(bl)
            self._canSlew.set(bl)
            self._canSlewAltAz.set(bl)
            self._canSlewAltAzAsync.set(bl)
            self._canSlewAsync.set(bl)
            self._canSync.set(bl)
            self._canSyncAltAz.set(bl)
            self._canUnpark.set(bl)
            self._canMovePrimaryAxis.set(bl)
            self._canMoveSecondaryAxis.set(bl)
            self._primaryAxisRates = []
            self._secondaryAxisRates = []
            self._ClearFrame(self._primaryAxisFrame)
            self._ClearFrame(self._secondaryAxisFrame)
        else:
            # we are connected, so display the values from the passed
            # object

            self._canFindHome.set(str(caps.CanFindHome))
            self._canPark.set(str(caps.CanPark))
            self._canPulseGuide.set(str(caps.CanPulseGuide))
            self._canSetDeclinationRate.set(str(caps.CanSetDeclinationRate))
            self._canSetGuideRates.set(str(caps.CanSetGuideRates))
            self._canSetPark.set(str(caps.CanSetPark))
            self._canSetPierSide.set(str(caps.CanSetPierSide))
            self._canSetRightAscensionRate.set(str(caps.CanSetRightAscensionRate))
            self._canSetTracking.set(str(caps.CanSetTracking))
            self._canSlew.set(str(caps.CanSlew))
            self._canSlewAltAz.set(str(caps.CanSlewAltAz))
            self._canSlewAltAzAsync.set(str(caps.CanSlewAltAzAsync))
            self._canSlewAsync.set(str(caps.CanSlewAsync))
            self._canSync.set(str(caps.CanSync))
            self._canSyncAltAz.set(str(caps.CanSyncAltAz))
            self._canUnpark.set(str(caps.CanUnpark))
            self._canMovePrimaryAxis.set(str(caps.CanMovePrimaryAxis))
            self._canMoveSecondaryAxis.set(str(caps.CanMoveSecondaryAxis))

            # to start with, the axis rate group boxes are empty and we don't know
            # how many rate ranges the driver supports, so we need to create them
            # from scratch when we read them from the driver

            # display the rate ranges in red

            style = ttk.Style()
            style.configure("ValueText.TLabel", foreground="red")

            # build the list of primary axis rate ranges

            self._primaryAxisRates = []

            for rate in caps.PrimaryAxisRates:
                minStr = locale.format_string("%.5f", rate.Minimum)
                maxStr = locale.format_string("%.5f", rate.Maximum)
                self._primaryAxisRates.append(f"{minStr} - {maxStr}")

            # create the labels, bind them to the elements in the list
            # of rate ranges, and add them to the group box frame

            n = len(self._primaryAxisRates)

            for i in range(n):
                lbl = ttk.Label(
                    self._primaryAxisFrame,
                    text=self._primaryAxisRates[i],
                    style="ValueText.TLabel",
                )
                lbl.grid(row=i, column=0)

            # build the list of secondary axis rate ranges

            self._secondaryAxisRates = []

            for rate in caps.SecondaryAxisRates:
                minStr = locale.format_string("%.5f", rate.Minimum)
                maxStr = locale.format_string("%.5f", rate.Maximum)
                self._secondaryAxisRates.append(f"{minStr} - {maxStr}")

            # create the labels, bind them to the elements in the list
            # of rate ranges, and add them to the group box frame

            n = len(self._secondaryAxisRates)

            for i in range(n):
                lbl = ttk.Label(
                    self._secondaryAxisFrame,
                    text=self._secondaryAxisRates[i],
                    style="ValueText.TLabel",
                )
                lbl.grid(row=i, column=0)

    def _ClearFrame(self, frame):
        # remove all the widgets from the passed frame

        for widget in frame.winfo_children():
            widget.destroy()

    # End of Private Properties and Methods
