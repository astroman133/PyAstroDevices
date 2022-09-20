from alpaca.telescope import *  # Multiple Classes including Enumerations

from app_settings import ApplicationSettings


class TelescopeParameters:
    """
    Class to contain properties that are read from the telescope and not
    changed by the application. The initializer has the abilty to create an
    empty instance, or one with values read from the driver.
    """

    def __init__(self, telescope=None):
        self._telescope = telescope

        if telescope:
            # populate this instance with values read from the telescope driver

            self._alignmentMode = telescope.AlignmentMode
            self._apertureArea = telescope.ApertureArea
            self._apertureDiameter = telescope.ApertureDiameter
            self._description = telescope.Description
            self._doesRefraction = telescope.DoesRefraction
            self._driverInfo = telescope.DriverInfo
            self._driverVersion = telescope.DriverVersion
            self._equatorialSystem = telescope.EquatorialSystem
            self._focalLength = telescope.FocalLength
            self._guideRateDeclination = telescope.GuideRateDeclination
            self._guideRateRightAscension = telescope.GuideRateRightAscension
            self._interfaceVersion = telescope.InterfaceVersion
            self._name = telescope.Name
            self._siteElevation = telescope.SiteElevation
            self._siteLatitude = telescope.SiteLatitude
            self._siteLongitude = telescope.SiteLongitude
            self._slewSettleTime = telescope.SlewSettleTime
            self._supportedActions = telescope.SupportedActions
            self._trackingRates = telescope.TrackingRates
        else:
            # create an instance populated with initial/default values

            self._alignmentMode = AlignmentModes.algGermanPolar
            self._apertureArea = float("nan")
            self._apertureDiameter = float("nan")
            self._description = ""
            self._driverInfo = ""
            self._doesRefraction = False
            self._driverVersion = ""
            self._equatorialSystem = EquatorialCoordinateType.equTopocentric
            self._focalLength = float("nan")
            self._guideRateDeclination = 0.0
            self._guideRateRightAscension = 0.0
            self._interfaceVersion = 0
            settings = ApplicationSettings.GetInstance()
            self._name = settings.TelescopeDriverName
            self._siteElevation = float("nan")
            self._siteLatitude = float("nan")
            self._siteLongitude = float("nan")
            self._slewSettleTime = 0
            self._supportedActions = []
            self._trackingRates = []
            self._trackingRates.append(DriveRates.driveSidereal)

    @property
    def IsConnected(self):
        if self._telescope is None:
            return False
        else:
            return True

    @property
    def AlignmentMode(self):
        return self._alignmentMode

    @property
    def ApertureArea(self):
        return self._apertureArea

    @property
    def ApertureDiameter(self):
        return self._apertureDiameter

    @property
    def Description(self):
        return self._description

    @property
    def DriverInfo(self):
        return self._driverInfo

    @property
    def DriverVersion(self):
        return self._driverVersion

    @property
    def DoesRefraction(self):
        return self._doesRefraction

    @property
    def EquatorialSystem(self):
        return self._equatorialSystem

    @property
    def FocalLength(self):
        return self._focalLength

    @property
    def GuideRateDeclination(self):
        return self._guideRateDeclination

    @property
    def GuideRateRightAscension(self):
        return self._guideRateRightAscension

    @property
    def InterfaceVersion(self):
        return self._interfaceVersion

    @property
    def Name(self):
        return self._name

    @property
    def SiteElevation(self):
        return self._siteElevation

    @property
    def SiteLatitude(self):
        return self._siteLatitude

    @property
    def SiteLongitude(self):
        return self._siteLongitude

    @property
    def SlewSettleTime(self):
        return self._slewSettleTime

    # @property
    # def SupportedActions(self):
    # 	return self._supportedActions

    @property
    def TrackingRates(self):
        return self._trackingRates
