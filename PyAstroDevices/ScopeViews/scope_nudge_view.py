import math

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from PIL import Image, ImageTk
from pubsub import pub

from alpaca.telescope import *  # Multiple Classes including Enumerations

from scope_status import TelescopeStatus
from scope_helpers import *
from exception_formatter import ExceptionFormatter


class TelescopeNudgeView:
    """
    This class manages the display and interaction of the widgets on the
    Telescope Motion tab page
    """

    _ERROR_TITLE = "Telescope Driver Error"

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
        self._trackingDisplay.set("off")
        self._sideOfPierDisplay = tk.StringVar(master=None)
        self._sideOfPierDisplay.set(nd)
        self._slewingFlagDisplay = tk.StringVar(master=None)
        self._slewingFlagDisplay.set(bl)
        self._parkingFlagDisplay = tk.StringVar(master=None)
        self._parkingFlagDisplay.set(bl)
        self._cwUpFlagDisplay = tk.StringVar(master=None)
        self._cwUpFlagDisplay.set(bl)
        self._atHomeFlagDisplay = tk.StringVar(master=None)
        self._atHomeFlagDisplay.set(bl)
        self._parkLabelDisplay = tk.StringVar(master=None)
        self._parkLabelDisplay.set("Park")
        self._moveAxisRatesDisplay = tk.StringVar(master=None)
        self._moveAxisRatesDisplay.set(bl)
        self._nudgeRates = []
        self._selectedNudgeRateDisplay = tk.StringVar(master=None)
        self._selectedNudgeRateDisplay.set(bl)
        self._isConnectedDisplay = tk.StringVar(master=None)
        self._isConnectedDisplay.set("Not Connected")

        self._nudgeBtnDisplay = []

        for b in range(4):
            self._nudgeBtnDisplay.append(tk.StringVar(master=None))

        self._SetNudgeButtonLabels()

        self._CreateWidgets()

        self._status = TelescopeStatus()

        # create the telescope status update listener

        pub.subscribe(self._StatusListener, "TelescopeStatusUpdate")
        pub.subscribe(self._ParmsListener, "TelescopeParametersUpdate")
        pub.subscribe(self._CapsListener, "TelescopeCapabilitiesUpdate")
        pub.subscribe(self._ScopeDisconnectListener, "ScopeDisconnect")

    # Start of Public Properties and Methods

    # End of Public Properties and Methods

    def _CreateWidgets(self):
        # create the widgets on the Telescope Nudge tab page

        # first create the widgets across the top of the Nudge tab page

        nudgeTopFrame = tk.Frame(self._parent)
        ttk.Label(nudgeTopFrame, text="Rate:").pack(side=tk.LEFT)

        self._nudgeRates_cbx = ttk.Combobox(
            nudgeTopFrame,
            values=self._nudgeRates,
            textvariable=self._selectedNudgeRateDisplay,
            state="readonly",
        )
        self._nudgeRates_cbx.pack(side=tk.LEFT, padx=(2, 4))

        # create the Park button, give it a click handler, and set its
        # initial state as disabled

        self._parkBtn = ttk.Button(
            nudgeTopFrame,
            textvariable=self._parkLabelDisplay,
            command=self._OnParkButtonClick,
            state="disabled",
        )
        self._parkBtn.pack(side=tk.LEFT, padx=4)

        # create the meridian flip button and give it a click handler and
        # disable it if not supported.

        self._flipBtn = ttk.Button(
            nudgeTopFrame,
            text="Meridian Flip",
            command=self._OnMeridianFlipButtonClick,
            state="disabled",
        )
        self._flipBtn.pack(side=tk.LEFT, padx=(4, 0), ipadx=2)

        # now create the frames to hold the nudge controls, the label
        # frame (groupbox) to hold the state variables, and the other
        # actions label frame to hold the Set Park button

        nudgeBottomFrame = tk.Frame(self._parent)
        nudgeBottomFrame.grid_rowconfigure(0)
        nudgeBottomFrame.grid_rowconfigure(1)
        nudgeBottomFrame.grid_columnconfigure(0)
        nudgeBottomFrame.grid_columnconfigure(1)

        directionFrame = tk.Frame(nudgeBottomFrame)
        scopeStateFrame = tk.LabelFrame(nudgeBottomFrame, text="Telescope State")
        otherActionsFrame = tk.LabelFrame(nudgeBottomFrame, text="Other Actions")

        # add the buttons to the direction frame

        directionFrame.grid_rowconfigure(0, weight=1, uniform="dirGroup")
        directionFrame.grid_rowconfigure(1, weight=1, uniform="dirGroup")
        directionFrame.grid_rowconfigure(2, weight=1, uniform="dirGroup")
        directionFrame.grid_columnconfigure(0, weight=1, uniform="dirGroup")
        directionFrame.grid_columnconfigure(1, weight=1, uniform="dirGroup")
        directionFrame.grid_columnconfigure(2, weight=1, uniform="dirGroup")

        n_btn = ttk.Button(
            directionFrame, textvariable=self._nudgeBtnDisplay[0], width=3
        )
        n_btn.bind("<ButtonPress-1>", self._StartNudgeNorth)
        n_btn.bind("<ButtonRelease-1>", self._StopNudgeNorth)
        n_btn.grid(row=0, column=1, padx=2, pady=2, sticky="NEWS")

        w_btn = ttk.Button(
            directionFrame, textvariable=self._nudgeBtnDisplay[2], width=3
        )
        w_btn.bind("<ButtonPress-1>", self._StartNudgeWest)
        w_btn.bind("<ButtonRelease-1>", self._StopNudgeWest)
        w_btn.grid(row=1, column=0, padx=2, pady=2, sticky="NEWS")

        e_btn = ttk.Button(
            directionFrame, textvariable=self._nudgeBtnDisplay[3], width=3
        )
        e_btn.bind("<ButtonPress-1>", self._StartNudgeEast)
        e_btn.bind("<ButtonRelease-1>", self._StopNudgeEast)
        e_btn.grid(row=1, column=2, padx=2, pady=2, sticky="NEWS")

        s_btn = ttk.Button(
            directionFrame, textvariable=self._nudgeBtnDisplay[1], width=3
        )
        s_btn.bind("<ButtonPress-1>", self._StartNudgeSouth)
        s_btn.bind("<ButtonRelease-1>", self._StopNudgeSouth)
        s_btn.grid(row=2, column=1, padx=2, pady=2, sticky="NEWS")

        # create the Stop button and add the stop image to it

        image = Image.open("./assets/stop.png")
        image = image.resize((20, 20), Image.ANTIALIAS)
        self._stopIcon = ImageTk.PhotoImage(image)
        h_btn = ttk.Button(
            directionFrame, image=self._stopIcon, text=None, compound=tk.CENTER, width=0
        )
        h_btn.grid(row=1, column=1, padx=2, pady=2, sticky="NEWS")

        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")
        ttk.Label(
            scopeStateFrame,
            textvariable=self._isConnectedDisplay,
            style="ValueText.TLabel",
        ).pack(side=tk.TOP)

        self._trackingChkbox = ttk.Checkbutton(
            scopeStateFrame,
            text="Tracking",
            variable=self._trackingDisplay,
            command=self._SetTracking,
            onvalue="on",
            offvalue="off",
        )
        self._trackingChkbox.pack(side=tk.TOP)

        scopeStateValuesFrame = tk.Frame(scopeStateFrame)

        for r in range(7):
            scopeStateValuesFrame.grid_rowconfigure(r)

        for c in range(2):
            scopeStateValuesFrame.grid_columnconfigure(c, weight=1)

        ttk.Label(scopeStateValuesFrame, text="Sidereal Time:").grid(
            row=0, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="RA:").grid(row=1, column=0, sticky="E")
        ttk.Label(scopeStateValuesFrame, text="Dec:").grid(row=2, column=0, sticky="E")
        ttk.Label(scopeStateValuesFrame, text="Azimuth:").grid(
            row=3, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Altitude:").grid(
            row=4, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Hour Angle:").grid(
            row=5, column=0, sticky="E"
        )
        ttk.Label(scopeStateValuesFrame, text="Side of Pier:").grid(
            row=6, column=0, sticky="E"
        )

        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._siderealTimeDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=0, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._rightAscensionDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=1, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._declinationDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=2, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._azimuthDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=3, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._altitudeDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=4, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._hourAngleDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=5, column=1, sticky="W")
        ttk.Label(
            scopeStateValuesFrame,
            textvariable=self._sideOfPierDisplay,
            width=12,
            style="ValueText.TLabel",
        ).grid(row=6, column=1, sticky="W")

        scopeStateValuesFrame.pack(side=tk.TOP)

        labels1Frame = tk.Frame(scopeStateFrame)

        ttk.Label(
            labels1Frame,
            textvariable=self._slewingFlagDisplay,
            width=7,
            style="ValueText.TLabel",
        ).pack(side=tk.LEFT, padx=3)
        ttk.Label(
            labels1Frame,
            textvariable=self._parkingFlagDisplay,
            width=7,
            style="ValueText.TLabel",
        ).pack(side=tk.LEFT, padx=3)
        self._cwUpLabel = ttk.Label(
            labels1Frame,
            textvariable=self._cwUpFlagDisplay,
            width=10,
            style="ValueText.TLabel",
        )
        self._cwUpLabel.pack(side=tk.LEFT, padx=3)

        labels1Frame.pack(side=tk.TOP)

        labels2Frame = tk.Frame(scopeStateFrame)
        ttk.Label(labels2Frame,
            textvariable=self._atHomeFlagDisplay,
            width=9,
            style="ValueText.TLabel"
        ).pack(side=tk.LEFT, padx=3)

        labels2Frame.pack(side=tk.TOP)

        self._setParkBtn = ttk.Button(
            otherActionsFrame,
            text="Set Park",
            state=["disabled"],
            command=self._OnSetParkButtonClick,
        )
        self._setParkBtn.pack(side=tk.LEFT, padx=6, pady=6)

        self._findHomeBtn = ttk.Button(
            otherActionsFrame,
            text = "Find Home",
            command=self._OnFindHome
        )
        self._findHomeBtn.pack(side=tk.LEFT, padx=2, pady=6)
        self._HideFindHomeButton()

        # position bottom the child frames into their grid cells.

        scopeStateFrame.grid(row=0, column=0, rowspan=2, sticky="N", padx=6, pady=6)
        directionFrame.grid(row=0, column=1, sticky="N", padx=30, pady=(30, 20))
        otherActionsFrame.grid(row=1, column=1, sticky="N")

        nudgeTopFrame.pack(pady=3, side=tk.TOP, anchor="nw")
        nudgeBottomFrame.pack(side=tk.TOP, anchor="w", fill="x")
        self._parent.pack()

    def _ParmsListener(self, parms):
        # callback to handle messages with fresh parameters values

        self._parms = parms

        # adjust the nudge button labels based on the alignment mode

        self._SetNudgeButtonLabels()

    def _CapsListener(self, caps):
        # callback to handle message with fresh capabilities values

        self._caps = caps

        if self._caps.CanMovePrimaryAxis and self._caps.CanMoveSecondaryAxis:
            self._BuildNudgeRatesList()
        else:
            self._ClearNudgeRatesList()

        if self._caps.CanFindHome:
            self._ShowFindHomeButton()

    def _StatusListener(self, sts):
        # callback to handle message with fresh status values

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

        msg = "off"
        if sts.Tracking:
            msg = "on"
        self._trackingDisplay.set(msg)
        switch = PierSideSwitch(PierSide)
        self._sideOfPierDisplay.set(switch(sts.SideOfPier))

        # dis/enable the Park button

        state = ["disabled"]
        btnLabel = "Park"

        if sts.AtPark:
            btnLabel = "Unpark"

            if self._caps.CanUnpark:
                state = ["!disabled"]

            self._parkingFlagDisplay.set("Parked")
        else:  # here we are not parked
            # conditionally enable the Park button and hide the 'Parked' label

            if self._caps.CanPark and not sts.Slewing:
                state = ["!disabled"]
            self._parkingFlagDisplay.set("")

        self._parkLabelDisplay.set(btnLabel)
        self._parkBtn.state(state)

        # dis/enable the Meridian Flip button

        canFlip = False
        state = ["disabled"]

        # In order to enable the button, we must be connected to a
        # German Equatorial mount.
        # The mount must be not Slewing and not be parked
        # The mount must also tracking and in a Counterweight Up position.

        if sts.Connected and self._parms.AlignmentMode == AlignmentModes.algGermanPolar:
            isReadyToSlew = sts.Tracking and not sts.Slewing and not sts.AtPark
            canFlip = sts.IsCounterWeightUp and isReadyToSlew

        if canFlip:
            state = ["!disabled"]

        self._flipBtn.state(state)

        # hide/show the Slewing label (setting the text to an empty string
        # hides it)

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

        # hide/show the At Home flag

        text = ""

        if sts.AtHome:
            text = "At Home"

        self._atHomeFlagDisplay.set(text)

        # enable/disable the Set Park button

        state = ["disabled"]

        if self._caps.CanSetPark and sts.Slewing == False:
            state = ["!disabled"]

        self._setParkBtn.state(state)

        # enable/disable the Find Home button

        if self._caps.CanFindHome:
            state = ["disabled"]

            if not sts.Slewing and not sts.AtPark:
                state = ["!disabled"]

            self._findHomeBtn.state(state)

    def _ScopeDisconnectListener(self):
        # callback to handle disconnects

        self._isConnectedDisplay.set("Not Connected")

        self._SetNudgeButtonLabels()
        self._HideFindHomeButton()

    def _Blink(self, state, currentText, offText, onText):
        # manage blinking the counterweight up indicator

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

    def _SetTracking(self):
        # handle user-initiated changes to the tracking checkbox

        if self._mgr.IsConnected:

            msg = self._trackingDisplay.get()

            try:
                newstate = False
                if msg == "on":
                    newstate = True
                self._mgr.ChangeTrackingState(newstate)
            except Exception as e:
                msg = "Unable to change the state of the tracking flag."
                msg += "Details follow:\r\n\r\n"
                self._ShowExceptionError(self._ERROR_TITLE, msg, e)

                # return the checkbox to its original state

                state = "on" if (msg == "off") else "off"
                self._trackingDisplay.set(state)

    def _OnParkButtonClick(self):
        # click handler for the Park/Unpark button

        if self._status.AtPark and self._caps.CanUnpark:
            # here we are parked, and unparking is supported

            try:
                self._mgr.SetUnparkedState()

                self._parkLabelDisplay.set("Park")
                self._parkingFlagDisplay.set("")
            except Exception as e:
                msg = "Unable to Unpark the telescope. Details follow:\r\n\r\n"
                self._ShowExceptionError(self._ERROR_TITLE, msg, e)
        elif not self._status.AtPark and self._caps.CanPark:
            # here we are not parked, and parking is supported

            try:
                self._mgr.SlewToPark()
                self._parkingFlagDisplay.set("Parking")
            except Exception as e:
                msg = "Unable to Park the telescope. Details follow:\r\n\r\n"
                self._ShowExceptionError(self._ERROR_TITLE, msg, e)

    def _OnMeridianFlipButtonClick(self):
        # click handler for the Meridian Flip button

        # we should only get here if meridian flip is supported

        try:
            self._mgr.StartMeridianFlip()
        except Exception as e:
            msg = "Unable to start a meridian flip. Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)

    def _OnSetParkButtonClick(self):
        # click handler for the Set Park button

        try:
            self._mgr.SetParkPosition()
        except Exception as e:
            msg = "Unable to set the park position. Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)

    def _BuildNudgeRatesList(self):
        # use the primary axis rates to build a list of nudge rates.
        axisRates = self._caps.PrimaryAxisRates
        nudgeRates = NudgeRates.FromAxisRates(axisRates)

        strList = []

        if nudgeRates is not None and len(nudgeRates) > 0:
            for i in range(0, len(nudgeRates)):
                strList.append(nudgeRates[i].Name)

        if nudgeRates is not None:
            self._nudgeRates = nudgeRates
            self._nudgeRates_cbx["values"] = strList
            self._nudgeRates_cbx.current(0)

    def _SetNudgeButtonLabels(self):
        # assign labels to the nudge buttons based on the scope manager's
        # slew directions

        dirs = self._mgr.SlewDirections

        for b in range(4):
            text = dirs[b].Name
            self._nudgeBtnDisplay[b].set(text)

    def _ClearNudgeRatesList(self):
        # remove entries from the nudge rates combobox

        self._nudgeRates = None
        self._nudgeRates_cbx.set("")
        self._selectedNudgeRateDisplay.set("")

    def _StartNudgeNorth(self, event):
        # button press handler for the North/Up button

        self._StartNudge(NudgeDirection.North)

    def _StartNudgeSouth(self, event):
        # button press handler for the South/Down button

        self._StartNudge(NudgeDirection.South)

    def _StartNudgeEast(self, event):
        # button press handler for the East/Right button

        self._StartNudge(NudgeDirection.East)

    def _StartNudgeWest(self, event):
        # button press handler for the West/Left button

        self._StartNudge(NudgeDirection.West)

    def _StartNudge(self, direction):
        # nudge the scope in the specified direction

        try:
            # get the nudge rate, using the selected item in the nudge rates
            # combobox

            ndx = self._nudgeRates_cbx.current()
            rate = self._nudgeRates[ndx].Rate

            self._mgr.StartNudgeScope(direction, rate)
        except Exception as e:
            msg = "Unable to start nudging the telescope. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)

    def _StopNudgeNorth(self, event):
        # stop nudging the scope in the North direction

        self._StopNudge(NudgeDirection.North)

    def _StopNudgeSouth(self, event):
        # stop nudging the scope in the South direction

        self._StopNudge(NudgeDirection.South)

    def _StopNudgeEast(self, event):
        # stop nudging the scope in the East direction

        self._StopNudge(NudgeDirection.East)

    def _StopNudgeWest(self, event):
        # stop nudging the scope in the West direction

        self._StopNudge(NudgeDirection.West)

    def _StopNudge(self, direction):
        # stop nudging the telescope in the requested direction

        try:
            self._mgr.StopNudgeScope(direction)
        except Exception as e:
            msg = "Unable to stop nudging the telescope. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)
    
    def _ShowButton(self, widget, side, padx, pady):
        # unhide a widget
        widget.pack(side=side, padx=padx, pady=pady)

    def _HideButton(self, widget):
        # hide a widget
        widget.pack_forget()

    def _ShowFindHomeButton(self):
        # unhide the Find Home button

        self._ShowButton(self._findHomeBtn, side=tk.LEFT, padx=(0,6), pady=6)

    def _HideFindHomeButton(self):
        # hide the Find Home Button
        self._HideButton(self._findHomeBtn)

    def _OnFindHome(self):
        # handler for Find Home button click

        try:
            # for better or worse FindHome is synchronous and does not return until
            # the operation is complete so we need to show the hourglass cursor while it
            # is homing
            pub.sendMessage("change_cursor", wait=True)
            self._mgr.SeekHomePosition()
        except Exception as e:
            msg = "Unable to find the telescope's Home position. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)
        finally:
            pub.sendMessage("change_cursor", wait=False)

    def _ShowExceptionError(self, title, message, xcp):
        msg = message
        formatter = ExceptionFormatter.GetInstance()
        msg += formatter.Format(xcp)
        root = self._parent
        messagebox.showerror(title, msg, parent=root)

    # End of Private Properties and Methods
