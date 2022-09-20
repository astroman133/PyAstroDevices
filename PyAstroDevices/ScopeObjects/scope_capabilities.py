from alpaca.telescope import *  # Multiple Classes including Enumerations


class TelescopeCapabilities:
    """
    This class contains all the CanXXX properties of a telescope. These
    properties do not change and so only need to be read one time,
    immediately after connection. The initializer has the ability to
    create an empty instance, or one with values read from the driver.
    """

    def __init__(self, telescope=None):
        # instance initializer method

        self._telescope = telescope

        if telescope:
            # initialize our properties with fresh data from the driver

            self._canFindHome = telescope.CanFindHome
            self._canPark = telescope.CanPark
            self._canPulseGuide = telescope.CanPulseGuide
            self._canSetDeclinationRate = telescope.CanSetDeclinationRate
            self._canSetGuideRates = telescope.CanSetGuideRates
            self._canSetPark = telescope.CanSetPark
            self._canSetPierSide = telescope.CanSetPierSide
            self._canSetRightAscensionRate = telescope.CanSetRightAscensionRate
            self._canSetTracking = telescope.CanSetTracking
            self._canSlew = telescope.CanSlew
            self._canSlewAltAz = telescope.CanSlewAltAz
            self._canSlewAltAzAsync = telescope.CanSlewAltAzAsync
            self._canSlewAsync = telescope.CanSlewAsync
            self._canSync = telescope.CanSync
            self._canSyncAltAz = telescope.CanSyncAltAz
            self._canUnpark = telescope.CanUnpark
            self._canMovePrimaryAxis = telescope.CanMoveAxis(TelescopeAxes.axisPrimary)
            self._canMoveSecondaryAxis = telescope.CanMoveAxis(
                TelescopeAxes.axisSecondary
            )
            self._primaryAxisRates = telescope.AxisRates(TelescopeAxes.axisPrimary)
            self._secondaryAxisRates = telescope.AxisRates(TelescopeAxes.axisSecondary)
        else:
            # initialize our properties with default values

            self._canFindHome = False
            self._canPark = False
            self._canPulseGuide = False
            self._canSetDeclinationRate = False
            self._canSetGuideRates = False
            self._canSetPark = False
            self._canSetPierSide = False
            self._canSetRightAscensionRate = False
            self._canSetTracking = False
            self._canSlew = False
            self._canSlewAltAz = False
            self._canSlewAltAzAsync = False
            self._canSlewAsync = False
            self._canSync = False
            self._canSyncAltAz = False
            self._canUnpark = False
            self._canMovePrimaryAxis = False
            self._canMoveSecondaryAxis = False
            self._primaryAxisRates = []
            self._secondaryAxisRates = []

    @property
    def IsConnected(self):
        if self._telescope is None:
            return False
        else:
            return True

    @property
    def CanFindHome(self):
        return self._canFindHome

    @property
    def CanPark(self):
        return self._canPark

    @property
    def CanPulseGuide(self):
        return self._canPulseGuide

    @property
    def CanSetDeclinationRate(self):
        return self._canSetDeclinationRate

    @property
    def CanSetGuideRates(self):
        return self._canSetGuideRates

    @property
    def CanSetPark(self):
        return self._canSetPark

    @property
    def CanSetPierSide(self):
        return self._canSetPierSide

    @property
    def CanSetRightAscensionRate(self):
        return self._canSetRightAscensionRate

    @property
    def CanSetTracking(self):
        return self._canSetTracking

    @property
    def CanSlew(self):
        return self._canSlew

    @property
    def CanSlewAltAz(self):
        return self._canSlewAltAz

    @property
    def CanSlewAltAzAsync(self):
        return self._canSlewAltAzAsync

    @property
    def CanSlewAsync(self):
        return self._canSlewAsync

    @property
    def CanSync(self):
        return self._canSync

    @property
    def CanSyncAltAz(self):
        return self._canSyncAltAz

    @property
    def CanUnpark(self):
        return self._canUnpark

    @property
    def CanMovePrimaryAxis(self):
        return self._canMovePrimaryAxis

    @property
    def CanMoveSecondaryAxis(self):
        return self._canMoveSecondaryAxis

    @property
    def PrimaryAxisRates(self):
        return self._primaryAxisRates

    @property
    def SecondaryAxisRates(self):
        return self._secondaryAxisRates
