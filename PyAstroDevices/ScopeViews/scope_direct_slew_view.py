import locale

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from PIL import Image, ImageTk
from pubsub import pub

from alpaca.telescope import *  # Multiple Classes including Enumerations

from scope_status import TelescopeStatus
from scope_mgr import TelescopeManager
from scope_helpers import PierSideSwitch, Formatter, Validator
from float_entry_widget import FloatEntry
from float_entry_widget import FloatEntry


class TelescopeDirectSlewView:
    """
    This class manages the display and interaction of the widgets on the
    Telescope Direct Slew tab page
    """

    def __init__(self, parentFrame, scopeManager):
        # instance initializer
        self._parent = parentFrame
        self._mgr = scopeManager

        # create the variables that are bound to the U/I

        nd = "NO DATA"
        bl = ""
        self._altitudeDisplay = tk.StringVar(master=None)
        self._altitudeDisplay.set(nd)
        self._azimuthDisplay = tk.StringVar(master=None)
        self._azimuthDisplay.set(nd)
        self._declinationDisplay = tk.StringVar(master=None)
        self._declinationDisplay.set(nd)
        self._rightAscensionDisplay = tk.StringVar(master=None)
        self._rightAscensionDisplay.set(nd)
        self._siderealTimeDisplay = tk.StringVar(master=None)
        self._siderealTimeDisplay.set(nd)
        self._hourAngleDisplay = tk.StringVar(master=None)
        self._hourAngleDisplay.set(nd)
        self._trackingDisplay = tk.StringVar(master=None)
        self._trackingDisplay.set("Off")
        self._sideOfPierDisplay = tk.StringVar(master=None)
        self._sideOfPierDisplay.set(nd)
        self._slewingFlagDisplay = tk.StringVar(master=None)
        self._slewingFlagDisplay.set(bl)
        self._parkingFlagDisplay = tk.StringVar(master=None)
        self._parkingFlagDisplay.set(bl)
        self._cwUpFlagDisplay = tk.StringVar(master=None)
        self._cwUpFlagDisplay.set(bl)
        self._parkLabelDisplay = tk.StringVar(master=None)
        self._parkLabelDisplay.set("Park")
        self._moveAxisRatesDisplay = tk.StringVar(master=None)
        self._moveAxisRatesDisplay.set(bl)
        self._isConnectedDisplay = tk.StringVar(master=None)
        self._isConnectedDisplay.set("Not Connected")

        self._primaryAxisNameDisplay = tk.StringVar(master=None)
        self._primaryAxisNameDisplay.set("Target Right Ascension:")
        self._primaryAxisUnitsDisplay = tk.StringVar(master=None)
        self._primaryAxisUnitsDisplay.set("(hours)")
        self._secondaryAxisNameDisplay = tk.StringVar(master=None)
        self._secondaryAxisNameDisplay.set("Target Declination")
        self._secondaryAxisUnitsDisplay = tk.StringVar(master=None)
        self._secondaryAxisUnitsDisplay.set("(degrees)")
        self._primaryAxisTargetDisplay = tk.StringVar(master=None)
        self._primaryAxisTargetDisplay.set(bl)
        self._secondaryAxisTargetDisplay = tk.StringVar(master=None)
        self._secondaryAxisTargetDisplay.set(bl)

        self._CreateWidgets()

        self._status = TelescopeStatus()

        # create for the messages that we need to listen for

        pub.subscribe(self._StatusListener, "TelescopeStatusUpdate")
        pub.subscribe(self._ParmsListener, "TelescopeParametersUpdate")
        pub.subscribe(self._CapsListener, "TelescopeCapabilitiesUpdate")
        pub.subscribe(self._ScopeDisconnectListener, "ScopeDisconnect")
        pub.subscribe(self._DirectSlewSelectedListener, "DirectSlewActivated")

    # Start of Public Properties and Methods

    # End of Public Properties and Methods

    # Start of Private Properties and Methods

    def _CreateWidgets(self):
        # create the widgets on the Telescope Direct Slew tab page

        mainFrame = tk.Frame(self._parent)

        # now create the frame to hold the state variables

        scopeStateFrame = tk.LabelFrame(mainFrame, text="Telescope State")

        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")
        ttk.Label(
            scopeStateFrame,
            textvariable=self._isConnectedDisplay,
            style="ValueText.TLabel",
        ).pack(side=tk.TOP)

        scopeStateValuesFrame = tk.Frame(scopeStateFrame)

        for r in range(8):
            scopeStateValuesFrame.grid_rowconfigure(r)

        for c in range(2):
            scopeStateValuesFrame.grid_columnconfigure(c)

        ttk.Label(scopeStateValuesFrame, text="Tracking:").grid(
            row=0, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Sidereal Time:").grid(
            row=1, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="RA:").grid(
            row=2, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Dec:").grid(
            row=3, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Azimuth:").grid(
            row=4, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Altitude:").grid(
            row=5, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Hour Angle:").grid(
            row=6, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Side of Pier:").grid(
            row=7, column=0, sticky="E"
        )

        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._trackingDisplay,
            width=12,
           style="ValueText.TLabel",
        ).grid(row=0, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._siderealTimeDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=1, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._rightAscensionDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=2, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._declinationDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=3, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._azimuthDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=4, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._altitudeDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=5, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._hourAngleDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=6, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._sideOfPierDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=7, column=1, sticky="W")

        scopeStateValuesFrame.pack(side=tk.TOP)

        # create and populate the frame that displays the slewing and
        # counterweight up flags

        labelsFrame = tk.Frame(scopeStateFrame)

        ttk.Label(
            labelsFrame,
            textvariable=self._slewingFlagDisplay,
            width=7,
            style="ValueText.TLabel",
        ).pack(side=tk.LEFT, padx=3)
        ttk.Label(
            labelsFrame,
            textvariable=self._parkingFlagDisplay,
            width=7,
            style="ValueText.TLabel",
        ).pack(side=tk.LEFT, padx=3)
        self._cwUpLabel = ttk.Label(
            labelsFrame,
            textvariable=self._cwUpFlagDisplay,
            width=10,
            style="ValueText.TLabel",
        )
        self._cwUpLabel.pack(side=tk.LEFT, padx=3)

        labelsFrame.pack(side=tk.TOP)

        # create the labels and entry boxes to contain the target coordinates
        # of the slew

        scopeSlewFrame = tk.Frame(mainFrame)

        ttk.Label(scopeSlewFrame, textvariable=self._primaryAxisNameDisplay).grid(
            row=0, column=0, sticky="e", padx=3
        )
        ttk.Label(scopeSlewFrame, textvariable=self._primaryAxisUnitsDisplay).grid(
            row=1, column=0, sticky="e", padx=3
        )
        ttk.Label(scopeSlewFrame, textvariable=self._secondaryAxisNameDisplay).grid(
            row=2, column=0, sticky="e", padx=3, pady=(14, 0)
        )
        ttk.Label(scopeSlewFrame, textvariable=self._secondaryAxisUnitsDisplay).grid(
            row=3, column=0, sticky="e", padx=3
        )

        FloatEntry(
            scopeSlewFrame, width=12, textvariable=self._primaryAxisTargetDisplay
        ).grid(row=0, column=1, rowspan=2, sticky="w")
        FloatEntry(
            scopeSlewFrame, width=12, textvariable=self._secondaryAxisTargetDisplay
        ).grid(row=2, column=1, rowspan=2, sticky="w", pady=(14, 0))

        # create the Slew To Target and Stop buttons

        slewButtonsFrame = tk.Frame(scopeSlewFrame)

        ttk.Button(
            slewButtonsFrame, text="Slew To Target", command=self._StartDirectSlew
        ).pack(side=tk.LEFT, padx=(6, 0))
        image = Image.open("./assets/stop.png")
        image = image.resize((40, 40), Image.ANTIALIAS)
        self._stopIcon = ImageTk.PhotoImage(image)
        ttk.Button(
            slewButtonsFrame,
            image=self._stopIcon,
            text=None,
            width=0,
            compound=tk.CENTER,
            command=self._AbortSlew,
        ).pack(side=tk.LEFT, padx=(6, 0))

        slewButtonsFrame.grid(row=4, column=0, columnspan=2, pady=26)

        # position the child frames into their grid cells.

        scopeStateFrame.grid(row=0, column=0, sticky="N", padx=4, pady=4)
        scopeSlewFrame.grid(row=0, column=1, sticky="N", padx=4, pady=38)
        mainFrame.pack(side=tk.TOP, anchor="w", fill="x")

        self._parent.pack()

    def _ParmsListener(self, parms):
        # save fresh parameters sent from the scope manager

        self._parms = parms

    def _CapsListener(self, caps):
        # save fresh capabilities sent from the scope manager

        self._caps = caps

    def _StatusListener(self, sts):
        # save fresh status sent from the scope manager and update the bound
        # variables with the new values

        self._status = sts

        state = "Not Connected"

        if sts.Connected:
            state = "Connected"

        self._isConnectedDisplay.set(state)

        self._altitudeDisplay.set(Formatter.GetDegreesString(sts.Altitude))
        self._azimuthDisplay.set(Formatter.GetDegreesString(sts.Azimuth))
        self._declinationDisplay.set(Formatter.GetDegreesString(sts.Declination))
        self._rightAscensionDisplay.set(Formatter.GetTimeString(sts.RightAscension))
        self._siderealTimeDisplay.set(Formatter.GetTimeString(sts.SiderealTime))
        self._hourAngleDisplay.set(Formatter.GetTimeString(sts.HourAngle))

        msg = "Off"
        if sts.Tracking:
            msg = "On"
        self._trackingDisplay.set(msg)
        switch = PierSideSwitch(PierSide)
        self._sideOfPierDisplay.set(switch(sts.SideOfPier))

        # hide/show the Slewing label (setting the text to an empty
        # string hides it)

        text = ""

        if sts.Slewing:
            text = "Slewing"

        self._slewingFlagDisplay.set(text)

        # hide/show the Weight Up flag and cause it to blink

        text = ""

        if (
            sts.IsCounterWeightUp
            and self._parms.AlignmentMode == AlignmentModes.algGermanPolar
        ):
            text = "Weight Up"

        self._cwUpFlagDisplay.set(text)
        self._Blink(sts.IsCounterWeightUp, text, "", text)

        # change the labels for value entry based on whether we are tracking

        if sts.Tracking:
            self._primaryAxisNameDisplay.set("Target Right Ascension:")
            self._primaryAxisUnitsDisplay.set("(hours)")
            self._secondaryAxisNameDisplay.set("Target Declination:")
            self._secondaryAxisUnitsDisplay.set("(degrees)")
        else:
            self._primaryAxisNameDisplay.set("Target Azimuth:")
            self._primaryAxisUnitsDisplay.set("(degrees)")
            self._secondaryAxisNameDisplay.set("Target Altitude:")
            self._secondaryAxisUnitsDisplay.set("(degrees)")

    def _ScopeDisconnectListener(self):
        # handle disconnects from the device
        self._isConnectedDisplay.set("Not Connected")

    def _Blink(self, state, currentText, offText, onText):
        # manage blinking of the counterweight up indicator

        # if we are not cwup then just return

        if not state:
            return

        # if the U/I is showing 'Weight Up' the new text is blank

        newText = offText

        if currentText == offText:
            newText = onText

        self._cwUpFlagDisplay.set(newText)
        self._cwUpLabel.after(
            500,
            lambda: self._Blink(
                self._status.IsCounterWeightUp, newText, offText, onText
            ),
        )

    def _StartDirectSlew(self):
        # click handler for the Slew To Target button

        if self._status is None or self._status.Connected == False:
            return

        errorTitle = "Invalid Target Value Error"

        # get the contents of the target coordinates text boxes and
        # convert them to floats in a locale aware way.

        tstr = self._primaryAxisTargetDisplay.get()
        primaryTgt = locale.atof(tstr)
        tstr = self._secondaryAxisTargetDisplay.get()
        secondaryTgt = locale.atof(tstr)

        # validate that the entered values are in the correct range
        # report errors if invalid

        if self._status.Tracking:
            # do an RA/Dec slew
            if not Validator.InRange(primaryTgt, 0.0, True, 24.0, False):
                msg = "An invalid right ascension was entered.\r\n\r\n"
                msg += "It must be a number that is 0.0 or greater and less "
                msg += "than 24.0."
                messagebox.showerror(errorTitle, msg)
            elif not Validator.InRange(secondaryTgt, -90.0, True, 90.0, True):
                msg = "An invalid declination was entered.\r\n\r\n"
                msg += "It must be a number that is greater than or equal "
                msg += "to -90.0 and less than or equal to 90.0."
                messagebox.showerror(errorTitle, msg)
            else:
                try:
                    self._mgr.SlewToCoordinatesAsync(primaryTgt, secondaryTgt)
                except Exception as e:
                    title = "Direct Slew To Coordinates Error"
                    msg = "Unable to start the direct slew. "
                    msg += "Details follow:\r\n\r\n"
                    self._ShowExceptionError(title, msg, e)
        else:  # do an Az/Alt slew
            if not Validator.InRange(primaryTgt, 0.0, True, 360.0, False):
                msg = "An invalid azimuth was entered.\r\n\r\n"
                msg += "It must be a number that is 0.0 or greater "
                msg += "and less than 360.0."
                messagebox.showerror(errorTitle, msg)
            elif not Validator.InRange(secondaryTgt, -90.0, True, 90.0, True):
                msg = "An invalid altitude was entered.\r\n\r\n"
                msg += "It must be a number that is greater than or equal "
                msg += "to 0.0 and less than or equal to 90.0."
                messagebox.showerror(errorTitle, msg)
            else:
                try:
                    self._mgr.SlewToAltAzAsync(primaryTgt, secondaryTgt)
                except Exception as e:
                    title = "Direct Slew To Alt/Az Error"
                    msg = "Unable to start the direct slew. "
                    msg += "Details follow:\r\n\r\n"
                    self._ShowExceptionError(title, msg, e)

    def _AbortSlew(self):
        # immediately stop any slew in progress

        try:
            self._mgr.AbortSlew()
        except Exception as e:
            title = "Abort Slew Error"
            msg = "Unable to start the direct slew. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError(title, msg, e)

    def _DirectSlewSelectedListener(self):
        # this method is called when the Direct Slew notebook/tab page
        # becomes active it set up the form for either RA/Dec slew or an
        # Alt/Az slew, depending on the Tracking state of the mount

        if self._status is None or self._status.Connected == False:
            return

        # change the labels for value entry based on whether we are tracking
        # 	if true we are entering RA and Dec, if false we are entering Az
        # 	and Alt.
        # also set the values to the current values from the driver

        if self._status.Tracking:
            self._primaryAxisNameDisplay.set("Target Right Ascension:")
            self._primaryAxisUnitsDisplay.set("(hours)")
            targetStr = locale.format_string("%.5f", self._status.RightAscension)
            self._primaryAxisTargetDisplay.set(targetStr)

            self._secondaryAxisNameDisplay.set("Target Declination:")
            self._secondaryAxisUnitsDisplay.set("(degrees)")
            targetStr = locale.format_string("%.5f", self._status.Declination)
            self._secondaryAxisTargetDisplay.set(targetStr)
        else:
            self._primaryAxisNameDisplay.set("Target Azimuth:")
            self._primaryAxisUnitsDisplay.set("(degrees)")
            targetStr = locale.format_string("%.5f", self._status.Azimuth)
            self._primaryAxisTargetDisplay.set(targetStr)

            self._secondaryAxisNameDisplay.set("Target Altitude:")
            self._secondaryAxisUnitsDisplay.set("(degrees)")
            targetStr = locale.format_string("%.5f", self._status.Altitude)
            self._secondaryAxisTargetDisplay.set(targetStr)

    def _ShowExceptionError(self, title, message, xcp):
        msg = message
        formatter = ExceptionFormatter.GetInstance()
        msg += formatter.Format(xcp)
        root = self._parent
        messagebox.showerror(title, msg, parent=root)
