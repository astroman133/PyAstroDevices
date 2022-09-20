import locale
import math

import tkinter as tk
from tkinter import ttk
from pubsub import pub
from enum_switch import Switch
from alpaca.telescope import *  # Multiple Classes including Enumerations

from scope_parameters import TelescopeParameters
from scope_helpers import *


class AlignmentModeSwitch(Switch):
    """
    This class provides friendly names for the corresponding
    Alpaca Alignment Mode enumeration members
    """

    def algAltAz(self):
        return "Altitude-Azimuth"

    def algPolar(self):
        return "Equatorial"

    def algGermanPolar(self):
        return "German Equatorial"


class EquatorialSystemSwitch(Switch):
    """
    This class provides friendly names for the corresponding
    Alpaca Equatorial System enumeration members
    """

    def equOther(self):
        return "Other"

    def equTopocentric(self):
        return "Topocentric"

    def equJ2000(self):
        return "J2000"

    def equJ2050(self):
        return "J2050"

    def equB1950(self):
        return "B1950"

    def equLocalTopocentric(self):
        return "Topocentric"


class TelescopeParametersView(object):
    """
    This class manages the display and interaction of the widgets on the
    Telescope Static Properties tab page
    """

    def __init__(self, parentFrame):
        # instance initializer
        self._parent = parentFrame

        # create the variables that are bound to the U/I

        self._alignmentMode = tk.StringVar(master=None)
        self._apertureArea = tk.StringVar(master=None)
        self._apertureDiameter = tk.StringVar(master=None)
        self._description = tk.StringVar(master=None)
        self._doesRefraction = tk.StringVar(master=None)
        self._driverInfo = tk.StringVar(master=None)
        self._driverVersion = tk.StringVar(master=None)
        self._equatorialSystem = tk.StringVar(master=None)
        self._focalLength = tk.StringVar(master=None)
        self._guideRateDeclination = tk.StringVar(master=None)
        self._guideRateRightAscension = tk.StringVar(master=None)
        self._interfaceVersion = tk.StringVar(master=None)
        self._siteElevation = tk.StringVar(master=None)
        self._siteLatitude = tk.StringVar(master=None)
        self._siteLongitude = tk.StringVar(master=None)
        self._slewSettleTime = tk.StringVar(master=None)
        self._trackingRates = tk.StringVar(master=None)

        self._CreateWidgets()

        # fill the _parameters instance with default values and
        # populate the U/I

        self._parameters = TelescopeParameters()
        self._ParmsListener(self._parameters)

        # subscribe to parameters update messages

        pub.subscribe(self._ParmsListener, "TelescopeParametersUpdate")

    # Start of Public Properties and Methods

    # End of Public Properties and Methods

    # Start of Private Properties and Methods

    def _CreateWidgets(self):
        # create the widgets on the Telescope Parameters tab page

        # first create the main frame and divide it into two columns and
        # enough rows to hold all the parameters

        parmsFrame = tk.Frame(self._parent)

        for r in range(17):
            parmsFrame.grid_rowconfigure(r)

        for c in range(4):
            parmsFrame.grid_columnconfigure(c)

        # add the value labels to column 0

        ttk.Label(parmsFrame, text="Alignment mode:").grid(row=0, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Aperture Area (m2):").grid(
            row=1, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Aperture Diameter (m):").grid(
            row=2, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Description:").grid(row=3, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Does Refraction:").grid(row=4, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Driver Info:").grid(row=5, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Driver Version:").grid(row=6, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Equatorial System:").grid(
            row=7, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Focal Length (m):").grid(
            row=8, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text=f"Guide Rate Declination ({chr(176)}/sec):").grid(
            row=9, column=0, sticky="E"
        )
        ttk.Label(
            parmsFrame, text=f"Guide Rate Right Ascension ({chr(176)}/sec):"
        ).grid(row=10, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Interface Version:").grid(
            row=11, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Site Elevation (m):").grid(
            row=12, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Site Latitude:").grid(row=13, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Site Longitude:").grid(row=14, column=0, sticky="E")
        ttk.Label(parmsFrame, text="Slew Settle Time (sec):").grid(
            row=15, column=0, sticky="E"
        )
        ttk.Label(parmsFrame, text="Tracking Rates:").grid(row=16, column=0, sticky="E")

        # add the value labels, styled with red text, to column 1

        style = ttk.Style()
        style.configure("ValueText.TLabel", foreground="red")
        ttk.Label(
            parmsFrame, textvariable=self._alignmentMode, style="ValueText.TLabel"
        ).grid(row=0, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._apertureArea, style="ValueText.TLabel"
        ).grid(row=1, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._apertureDiameter, style="ValueText.TLabel"
        ).grid(row=2, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._description, style="ValueText.TLabel"
        ).grid(row=3, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._doesRefraction, style="ValueText.TLabel"
        ).grid(row=4, column=1, sticky="W")

        infoFrame = tk.Frame(parmsFrame)
        infoFrame.grid_rowconfigure(0)
        infoFrame.grid_rowconfigure(1)
        infoFrame.grid_columnconfigure(0)
        infoFrame.grid_columnconfigure(0)

        self._driverInfoList = tk.Listbox(
            infoFrame,
            listvariable=self._driverInfo,
            height=6,
            width=32,
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

        infoFrame.grid(row=5, column=1, sticky="w")

        ttk.Label(
            parmsFrame, textvariable=self._driverVersion, style="ValueText.TLabel"
        ).grid(row=6, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._equatorialSystem, style="ValueText.TLabel"
        ).grid(row=7, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._focalLength, style="ValueText.TLabel"
        ).grid(row=8, column=1, sticky="W")
        ttk.Label(
            parmsFrame,
            textvariable=self._guideRateDeclination,
            style="ValueText.TLabel",
        ).grid(row=9, column=1, sticky="W")
        ttk.Label(
            parmsFrame,
            textvariable=self._guideRateRightAscension,
            style="ValueText.TLabel",
        ).grid(row=10, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._interfaceVersion, style="ValueText.TLabel"
        ).grid(row=11, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._siteElevation, style="ValueText.TLabel"
        ).grid(row=12, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._siteLatitude, style="ValueText.TLabel"
        ).grid(row=13, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._siteLongitude, style="ValueText.TLabel"
        ).grid(row=14, column=1, sticky="W")
        ttk.Label(
            parmsFrame, textvariable=self._slewSettleTime, style="ValueText.TLabel"
        ).grid(row=15, column=1, sticky="W")
        lb = tk.Listbox(
            parmsFrame,
            listvariable=self._trackingRates,
            height=4,
            state=tk.DISABLED,
            disabledforeground="red",
        )
        lb.grid(row=16, column=1, sticky="W")

        parmsFrame.pack(pady=3, side=tk.TOP, anchor="nw", fill="x")
        self._parent.pack()

    def _ParmsListener(self, parms):
        # callback to handle receipt of fresh parameter values

        self._parameters = parms

        if not parms.IsConnected:
            # initialize the members

            bl = ""
            self._alignmentMode.set(bl)
            self._apertureArea.set(bl)
            self._apertureDiameter.set(bl)
            self._description.set(bl)
            self._doesRefraction.set(bl)
            self._driverInfo.set(bl)
            self._driverVersion.set(bl)
            self._equatorialSystem.set(bl)
            self._focalLength.set(bl)
            self._guideRateDeclination.set(bl)
            self._guideRateRightAscension.set(bl)
            self._interfaceVersion.set(bl)
            self._siteElevation.set(bl)
            self._siteLatitude.set(bl)
            self._siteLongitude.set(bl)
            self._slewSettleTime.set(bl)
            self._trackingRates.set(bl)
        else:
            bl = ""
            switch = AlignmentModeSwitch(AlignmentModes)
            self._alignmentMode.set(switch(parms.AlignmentMode))
            self._apertureArea.set(self._FormatFloat(parms.ApertureArea, 5))
            self._apertureDiameter.set(self._FormatFloat(parms.ApertureDiameter, 3))
            self._description.set(parms.Description)
            self._doesRefraction.set(str(parms.DoesRefraction))
            self._driverInfo.set(parms.DriverInfo)
            self._driverVersion.set(parms.DriverVersion)
            switch = EquatorialSystemSwitch(EquatorialCoordinateType)
            self._equatorialSystem.set(switch(parms.EquatorialSystem))
            self._focalLength.set(self._FormatFloat(parms.FocalLength, 3))
            self._guideRateDeclination.set(
                self._FormatFloat(parms.GuideRateDeclination, 5)
            )
            self._guideRateRightAscension.set(
                self._FormatFloat(parms.GuideRateRightAscension, 5)
            )
            self._interfaceVersion.set(str(parms.InterfaceVersion))
            self._siteElevation.set(self._FormatFloat(parms.SiteElevation, 0))
            #self._siteLatitude.set(self._FormatDegrees(parms.SiteLatitude))
            #self._siteLongitude.set(self._FormatDegrees(parms.SiteLongitude))
            self._siteLatitude.set(Formatter.GetDegreesString(parms.SiteLatitude))
            self._siteLongitude.set(Formatter.GetDegreesString(parms.SiteLongitude))
            self._slewSettleTime.set(str(parms.SlewSettleTime))
            switch = DriveRatesSwitch(DriveRates)
            rates = []

            for rate in parms.TrackingRates:
                if rate == DriveRates.driveSidereal:
                    rates.append(switch.driveSidereal())
                    continue

                if rate == DriveRates.driveKing:
                    rates.append(switch.driveKing())
                    continue

                if rate == DriveRates.driveLunar:
                    rates.append(switch.driveLunar())
                    continue

                if rate == DriveRates.driveSolar:
                    rates.append(switch.driveSolar())

            self._trackingRates.set(value=rates)

    def _FormatFloat(self, realValue, decimals):
        fmt = f"%.{decimals}f"
        return locale.format_string(fmt, realValue)

    # End of Private Properties and Methods
