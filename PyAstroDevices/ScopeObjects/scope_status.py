from alpaca.telescope import *  # Multiple Classes including Enumerations


class TelescopeStatus:
    """
    Class to contain properties that are periodically read from the telescope
    and are subject to change over time. The initializer has the ability to
    create an empty instance, or one with values read from the driver.
    """

    def __init__(self, telescope=None):
        if telescope:
            # populate this instance with values read from the telescope driver

            self._altitude = telescope.Altitude
            self._atHome = telescope.AtHome
            self._azimuth = telescope.Azimuth
            self._connected = telescope.Connected
            self._declination = telescope.Declination
            self._declinationRate = telescope.DeclinationRate
            self._guideRateDeclination = telescope.GuideRateDeclination
            self._guideRateRightAscension = telescope.GuideRateRightAscension
            self._isPulseGuiding = telescope.IsPulseGuiding
            self._rightAscension = telescope.RightAscension
            self._rightAscensionRate = telescope.RightAscensionRate
            self._sideOfPier = telescope.SideOfPier
            self._siderealTime = telescope.SiderealTime

            # reading AtPark or Slewing could raise an exception

            try:
                self._atPark = telescope.AtPark
                self._slewing = telescope.Slewing
            except:
                self._slewing = False
                raise

            # reading the target coordinates before they have been set will
            # raise an exception

            try:
                self._targetDeclination = telescope.TargetDeclination
            except:
                self._targetDeclination = float("nan")

            try:
                self._targetRightAscension = telescope.TargetRightAscension
            except:
                self._targetRightAscension = float("nan")

            self._tracking = telescope.Tracking
            self._trackingRate = telescope.TrackingRate
            self._hourAngle = self._CalculateHourAngle(
                self._siderealTime, self._rightAscension
            )
            self._isCwUp = self._CalculateCounterWeightUp(
                self._sideOfPier, self._hourAngle
            )
        else:
            # create an instance populated with initial/default values

            self._altitude = float("nan")
            self._atHome = False
            self._atPark = False
            self._azimuth = float("nan")
            self._connected = False
            self._declination = float("nan")
            self._declinationRate = 0.0
            self._guideRateDeclination = 0.0
            self._guideRateRightAscension = 0.0
            self._isPulseGuiding = False
            self._rightAscension = float("nan")
            self._rightAscensionRate = float("nan")
            self._sideOfPier = PierSide.pierUnknown
            self._siderealTime = float("nan")
            self._slewing = False
            self._targetDeclination = float("nan")
            self._targetRightAscension = float("nan")
            self._tracking = False
            self._trackingRate = DriveRates.driveSidereal
            self._hourAngle = float("nan")
            self._isCwUp = False

    @property
    def Altitude(self):
        return self._altitude

    @property
    def AtHome(self):
        return self._atHome

    @property
    def AtPark(self):
        return self._atPark

    @property
    def Azimuth(self):
        return self._azimuth

    @property
    def Connected(self):
        return self._connected

    @property
    def Declination(self):
        return self._declination

    @property
    def DeclinationRate(self):
        return self._declinationRate

    @property
    def GuideRateDeclination(self):
        return self._guideRateDeclination

    @property
    def GuideRateRightAscension(self):
        return self._guideRateRightAscension

    @property
    def IsPulseGuiding(self):
        return self._isPulseGuiding

    @property
    def RightAscension(self):
        return self._rightAscension

    @property
    def RightAscensionRate(self):
        return self._rightAscensionRate

    @property
    def SideOfPier(self):
        return self._sideOfPier

    @property
    def SiderealTime(self):
        return self._siderealTime

    @property
    def Slewing(self):
        return self._slewing

    @property
    def TargetDeclination(self):
        return self._targetDeclination

    @property
    def TargetRightAscension(self):
        return self._targetRightAscension

    @property
    def Tracking(self):
        return self._tracking

    @property
    def TrackingRate(self):
        return self._trackingRate

    @property
    def HourAngle(self):
        return self._hourAngle 

    @property
    def SideOfPier(self):
        return self._sideOfPier

    @property
    def IsCounterWeightUp(self):
        return self._isCwUp

    def _CalculateHourAngle(self, siderealTime, ra):
        retval = siderealTime - ra

        while retval < -12.0:
            retval += 24.0

        while retval > 12.0:
            retval -= 24.0

        return retval

    def _CalculateCounterWeightUp(self, pierSide, hourAngle):
        # The CW state is determined by looking at two things:  pier side
        # and hour angle (HA = LST – RA).
        # 	Pier Side = West;          0 > HA > -12              CW Down
        # 	Pier Side = East;          0 < HA < +12              CW Down

        # 	Pier Side = East;          0 > HA > -12              CW UP
        # 	Pier Side = West;          0 < HA < +12              CW UP

        retval = False

        if pierSide == PierSide.pierEast and -12 < hourAngle < 0:
            retval = True
        elif pierSide == PierSide.pierWest and 0 < hourAngle < 12:
            retval = True

        return retval
