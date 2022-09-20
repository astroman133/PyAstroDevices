import locale

import tkinter as tk
from tkinter import font as tkFont
from tkinter import ttk
from pubsub import pub
from alpaca.telescope import *  # Multiple Classes including Enumerations

from scope_status import TelescopeStatus
from scope_helpers import DriveRatesSwitch
from float_entry_widget import FloatEntry


class TelescopeTrackingRatesView:
    """
    This class manages the display and interaction of the widgets on the
    Telescope Tracking Rates tab page.
    """

    def __init__(self, parentFrame, scopeManager):
        # instance initializer

        self._parent = parentFrame
        self._mgr = scopeManager
        self._UTC_SECS_PER_SIDEREAL_SEC = 0.997269566334879

        self._rateUnits = (("ASCOM Units", "A"), ("JPL Horizons Units", "J"))

        # create the variables that are bound to the U/I

        bl = ""
        self._trackingRateMsgDisplay = tk.StringVar(master=None)
        self._trackingRateMsgDisplay.set("The tracking rate is not known.")

        self._currentRaRateDisplay = tk.StringVar(master=None)
        self._currentRaRateDisplay.set(bl)
        self._currentDecRateDisplay = tk.StringVar(master=None)
        self._currentDecRateDisplay.set(bl)
        self._newRatesUnitsDisplay = tk.StringVar(master=None)
        rate = self._rateUnits[0]
        self._newRatesUnitsDisplay.set(rate[1])
        self._raOffsetNewRateDisplay = tk.StringVar(master=None)
        self._raOffsetNewRateDisplay.set(bl)
        self._raOffsetNewUnitsDisplay = tk.StringVar(master=None)
        self._raOffsetNewUnitsDisplay.set("seconds / sidereal second")
        self._decOffsetNewRateDisplay = tk.StringVar(master=None)
        self._decOffsetNewRateDisplay.set(bl)
        self._decOffsetNewUnitsDisplay = tk.StringVar(master=None)
        self._decOffsetNewUnitsDisplay.set("arc-seconds / SI second")

        # add the widgets to the view

        self._CreateWidgets()

        # initialize the status object

        self._status = TelescopeStatus()

        # create the message handlers that we will use

        pub.subscribe(self._StatusListener, "TelescopeStatusUpdate")
        pub.subscribe(self._ParmsListener, "TelescopeParametersUpdate")
        pub.subscribe(self._CapsListener, "TelescopeCapabilitiesUpdate")
        pub.subscribe(self._ScopeDisconnectListener, "ScopeDisconnect")

    # Start of Public Methods

    # End of Public Methods

    # Start of Private Methods

    def _CreateWidgets(self):
        # create the widgets on the Telescope Tracking Rates tab
        # and arrange them in the frame

        # create a style that will display selected labels with red foreground

        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")

        ratesTopFrame = tk.Frame(self._parent)

        ratesTopFrame.grid_rowconfigure(0, weight=1)
        ratesTopFrame.grid_rowconfigure(1)
        ratesTopFrame.grid_rowconfigure(2)
        ratesTopFrame.grid_rowconfigure(3)
        ratesTopFrame.grid_columnconfigure(0, weight=1)

        ttk.Label(
            ratesTopFrame,
            textvariable=self._trackingRateMsgDisplay,
            style="ValueText.TLabel",
            font=("Arial", 12),
        ).grid(row=0, column=0, padx=6, pady=6, sticky="w")

        header = "Current Telescope Tracking Rate Offsets"
        currentRatesFrame = tk.LabelFrame(ratesTopFrame, text=header)

        currentRateValuesFrame = tk.Frame(currentRatesFrame)

        for r in range(3):
            currentRateValuesFrame.grid_rowconfigure(r)

        for c in range(3):
            currentRateValuesFrame.grid_columnconfigure(c)

        ttk.Label(currentRateValuesFrame, text="RA Offset Rate:").grid(
            row=0, column=0, sticky="e"
        )
        ttk.Label(
            currentRateValuesFrame,
            textvariable=self._currentRaRateDisplay,
            style="ValueText.TLabel",
        ).grid(row=0, column=1, sticky="w")
        ttk.Label(currentRateValuesFrame, text="seconds / sidereal second").grid(
            row=0, column=2, sticky="w"
        )

        ttk.Label(currentRateValuesFrame, text="Dec Offset Rate:").grid(
            row=1, column=0, sticky="e"
        )
        ttk.Label(
            currentRateValuesFrame,
            textvariable=self._currentDecRateDisplay,
            style="ValueText.TLabel",
        ).grid(row=1, column=1, sticky="w")
        ttk.Label(currentRateValuesFrame, text="arc-seconds / SI second").grid(
            row=1, column=2, sticky="w"
        )

        lblValue = "These offsets are only applied when the tracking rate is "
        lblValue += "set to Sidereal."
        ttk.Label(currentRateValuesFrame, text=lblValue).grid(
            row=2, column=0, columnspan=3
        )

        currentRateValuesFrame.pack(side=tk.TOP)
        currentRatesFrame.grid(row=1, column=0, sticky="w", padx=6)

        # create the rate buttons

        rateButtonsFrame = tk.Frame(ratesTopFrame)
        rateButtonsFrame.grid_rowconfigure(0)

        for c in range(6):
            rateButtonsFrame.grid_columnconfigure(c, weight=1)

        switch = DriveRatesSwitch(DriveRates)
        font = tkFont.Font(family="Arial", size=10)
        bsize = 50
        self._blankImage = tk.PhotoImage()

        btemp = tk.Button(
            rateButtonsFrame,
            text=switch.driveSidereal(),
            image=self._blankImage,
            state="disabled",
            font=font,
            compound=tk.CENTER,
            command=self._OnSiderealRateClick,
        )
        btemp.config(height=bsize, width=bsize)
        btemp.grid(row=0, column=1, sticky="NWSE", padx=4, pady=10)
        self._siderealRateBtn = btemp

        btemp = tk.Button(
            rateButtonsFrame,
            text=switch.driveLunar(),
            image=self._blankImage,
            state="disabled",
            font=font,
            compound=tk.CENTER,
            command=self._OnLunarRateClick,
        )
        btemp.config(height=bsize, width=bsize)
        btemp.grid(row=0, column=2, sticky="NWSE", padx=4, pady=10)
        self._lunarRateBtn = btemp

        btemp = tk.Button(
            rateButtonsFrame,
            text=switch.driveSolar(),
            image=self._blankImage,
            state="disabled",
            font=font,
            compound=tk.CENTER,
            command=self._OnSolarRateClick,
        )
        btemp.config(height=bsize, width=bsize)
        btemp.grid(row=0, column=3, sticky="NWSE", padx=4, pady=10)
        self._solarRateBtn = btemp

        btemp = tk.Button(
            rateButtonsFrame,
            text=switch.driveKing(),
            image=self._blankImage,
            state="disabled",
            font=font,
            compound=tk.CENTER,
            command=self._OnKingRateClick,
        )
        btemp.config(height=bsize, width=bsize)
        btemp.grid(row=0, column=4, sticky="NWSE", padx=4, pady=10)
        self._kingRateBtn = btemp

        # create and populate the groupbox that contains the widgets for
        # entering new tracking rates. It also contains the radio buttons
        # that specify whether the rates will be entered in JPL Horizons or
        # ASCOM units.

        changeRatesFrame = tk.LabelFrame(
            ratesTopFrame, text="Change Sidereal Tracking Offsets"
        )

        for r in range(3):
            changeRatesFrame.grid_rowconfigure(r)

        for c in range(4):
            changeRatesFrame.grid_columnconfigure(c)

        unitsFrame = tk.Frame(changeRatesFrame)

        # define the units radio buttons

        ttk.Label(unitsFrame, text="Rate Units:").pack(side=tk.LEFT, padx=4)
        rate = self._rateUnits[0]
        self._useAscomUnitsRadioButton = ttk.Radiobutton(
            unitsFrame,
            text=rate[0],
            value=rate[1],
            variable=self._newRatesUnitsDisplay,
            command=self._OnUnitsChanged,
        )
        self._useAscomUnitsRadioButton.pack(side=tk.LEFT, padx=4)

        rate = self._rateUnits[1]
        ttk.Radiobutton(
            unitsFrame,
            text=rate[0],
            value=rate[1],
            variable=self._newRatesUnitsDisplay,
            command=self._OnUnitsChanged,
        ).pack(side=tk.LEFT, padx=4)

        # create the labels and entry boxes for new offset rates
        # as well as a button to trigger sending the new rates to
        # the telescope

        unitsFrame.grid(row=0, column=0, columnspan=4, pady=6, sticky="w")

        ttk.Label(changeRatesFrame, text="RA Offset Rate:").grid(
            row=1, column=0, sticky="e", pady=4
        )
        FloatEntry(
            changeRatesFrame, width=10, textvariable=self._raOffsetNewRateDisplay
        ).grid(row=1, column=1, sticky="w", padx=6)
        ttk.Label(
            changeRatesFrame, textvariable=self._raOffsetNewUnitsDisplay, width=24
        ).grid(row=1, column=2, sticky="w")

        ttk.Label(changeRatesFrame, text="Dec Offset Rate:").grid(
            row=2, column=0, sticky="e", pady=4
        )
        FloatEntry(
            changeRatesFrame, width=10, textvariable=self._decOffsetNewRateDisplay
        ).grid(row=2, column=1, sticky="w", padx=6)
        ttk.Label(
            changeRatesFrame, textvariable=self._decOffsetNewUnitsDisplay, width=24
        ).grid(row=2, column=2, sticky="w")

        btemp = tk.Button(
            changeRatesFrame,
            text="Send To\nTelescope",
            image=self._blankImage,
            state="disabled",
            font=font,
            compound=tk.CENTER,
            command=self._OnSendNewRates,
        )
        bsize = 66
        btemp.config(height=bsize, width=bsize)
        btemp.grid(row=0, column=3, rowspan=3, sticky="NE", pady=10)
        self._sendBtn = btemp

        rateButtonsFrame.grid(row=2, column=0, padx=60, sticky="w")
        changeRatesFrame.grid(row=3, column=0, sticky="wn", ipadx=6, padx=6, pady=6)
        ratesTopFrame.pack(side=tk.TOP, anchor="nw", fill="x")
        self._parent.pack()

    def _ParmsListener(self, parms):
        # callback to handle parameters updates

        self._parms = parms

        if DriveRates.driveSidereal in parms.TrackingRates:
            self._siderealRateBtn["state"] = tk.NORMAL
        if DriveRates.driveLunar in parms.TrackingRates:
            self._lunarRateBtn["state"] = tk.NORMAL
        if DriveRates.driveSolar in parms.TrackingRates:
            self._solarRateBtn["state"] = tk.NORMAL
        if DriveRates.driveKing in parms.TrackingRates:
            self._kingRateBtn["state"] = tk.NORMAL

    def _CapsListener(self, caps):
        # callback to handle capabilities updates

        self._caps = caps

        if caps.CanSetRightAscensionRate and caps.CanSetDeclinationRate:
            self._sendBtn["state"] = tk.NORMAL

    def _StatusListener(self, sts):
        # callback to handle status updates

        self._status = sts

        switch = DriveRatesSwitch(DriveRates)
        rateName = "Unknown"
        match sts.TrackingRate:
            case DriveRates.driveSidereal:
                rateName = switch.driveSidereal()

            case DriveRates.driveLunar:
                rateName = switch.driveLunar()
                self._lunarRateBtn["state"] = tk.NORMAL

            case DriveRates.driveSolar:
                rateName = switch.driveSolar()
                self._solarRateBtn["state"] = tk.NORMAL

            case DriveRates.driveKing:
                rateName = switch.driveKing()

        msg = f"Currently tracking at the {rateName} rate."
        self._trackingRateMsgDisplay.set(msg)

        rateStr = locale.format_string("%.7f", sts.RightAscensionRate)
        self._currentRaRateDisplay.set(rateStr)
        rateStr = locale.format_string("%.7f", sts.DeclinationRate)
        self._currentDecRateDisplay.set(rateStr)

    def _ScopeDisconnectListener(self):
        # callback to handle disconnect logic

        self._trackingRateMsgDisplay.set("The tracking rate is not known.")
        self._currentRaRateDisplay.set("")
        self._currentDecRateDisplay.set("")
        self._siderealRateBtn["state"] = tk.DISABLED
        self._lunarRateBtn["state"] = tk.DISABLED
        self._solarRateBtn["state"] = tk.DISABLED
        self._kingRateBtn["state"] = tk.DISABLED
        self._sendBtn["state"] = tk.DISABLED

        rate = self._rateUnits[0]
        self._newRatesUnitsDisplay.set(rate[1])
        self._raOffsetNewUnitsDisplay.set("seconds / sidereal second")
        self._decOffsetNewUnitsDisplay.set("arc-seconds / SI second")

    def _OnUnitsChanged(self):
        # radio button click handler for the ASCOM and JPL Horizons unit
        # changes

        if not self._status.Connected:
            return
        self._raOffsetNewRateDisplay.set("")
        self._decOffsetNewRateDisplay.set("")

        if self._newRatesUnitsDisplay.get() == "A":
            # use ASCOM Units
            self._raOffsetNewUnitsDisplay.set("seconds / sidereal second")
            self._decOffsetNewUnitsDisplay.set("arc-seconds / SI second")
        else:  # use JPL Horizons Units
            self._raOffsetNewUnitsDisplay.set("arc-seconds / hour")
            self._decOffsetNewUnitsDisplay.set("arc-seconds / hour")

    def _ConvertTrackingRate(self, rate, isRaRate):
        # convert a tracking rate between NASA JPL Horizons units and
        # ASCOM Units

        factor = 1.0 / 3600.0  # assume the declinaton rate

        if isRaRate == True:  # set the factor for adjusting the RA rate
            factor = self._UTC_SECS_PER_SIDEREAL_SEC / (15.0 * 3600.0)

        return rate * factor

    def _OnSendNewRates(self):
        # button click handler to send new tracking rate offset values to
        # the telescope driver

        inNasaJplRates = False

        if self._newRatesUnitsDisplay.get() == "J":
            inNasaJplRates = True

        newRaRate = 0.0
        newDecRate = 0.0

        if self._caps.CanSetRightAscensionRate:
            rateStr = self._raOffsetNewRateDisplay.get()
            rate = locale.atof(rateStr)

            if inNasaJplRates:
                newRaRate = self._ConvertTrackingRate(rate, True)
            else:
                newRaRate = rate

        if self._caps.CanSetDeclinationRate:
            rateStr = self._decOffsetNewRateDisplay.get()
            rate = locale.atof(rateStr)

            if inNasaJplRates:
                # The entered rate is in NASA JPL Horizons units, so
                # convert to ASCOM units
                newDecRate = self._ConvertTrackingRate(rate, False)
            else:
                # the entered rate is already in ASCOM units so no
                # conversion needed
                newDecRate = rate

        try:
            self._mgr.SetOffsetTrackingRates(newRaRate, newDecRate)
        except Exception as e:
            msg = "Unable send new offset tracking rates to the telescope. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)

    def _OnSiderealRateClick(self):
        # click hander for the Sidereal rate button

        self._SetTrackingRate(DriveRates.driveSidereal)

    def _OnLunarRateClick(self):
        # click hander for the Lunar rate button

        self._SetTrackingRate(DriveRates.driveLunar)

    def _OnSolarRateClick(self):
        # click hander for the Solar rate button

        self._SetTrackingRate(DriveRates.driveSolar)

    def _OnKingRateClick(self):
        # click hander for the King rate button

        self._SetTrackingRate(DriveRates.driveKing)

    def _SetTrackingRate(self, driveRate):
        try:
            self._mgr.SetTrackingRate(driveRate)
        except Exception as e:
            msg = "Unable change the telescope's tracking rate. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)

    # End of Private Methods
