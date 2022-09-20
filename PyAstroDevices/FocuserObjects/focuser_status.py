from alpaca.focuser import *


class FocuserStatus:
    """
    Class to contain properties that are periodically read from the focuser
    and are subject to change over time. The initializer has the ability to
    create an empty instance, or one with values read from the driver.
    """

    def __init__(self, focuser=None):
        # Initialize the object instance

        if focuser:
            # populate this instance with values read from the focuser driver

            self._connected = focuser.Connected
            self._isMoving = focuser.IsMoving

            # reading the Position will raise an error if the focuser
            # is not Absolute

            try:
                self._position = focuser.Position
            except:
                self._position = float("nan")

            # reading TemperatureCompensation will raise an error if
            # the focuser does not support temp comp

            try:
                self._tempComp = focuser.TempComp
            except:
                self._tempComp = False

            # readint the Temperature will raise an exception if the
            # focuser does not support this capability.

            try:
                self._temperature = focuser.Temperature
            except:
                self._temperature = float("nan")
        else:
            # create an instance populated with initial/default values

            self._connected = False
            self._isMoving = False
            self._position = float("nan")
            self._tempComp = False
            self._temperature = float("nan")

    @property
    def Connected(self):
        return self._connected

    @property
    def IsMoving(self):
        return self._isMoving

    @property
    def Position(self):
        return self._position

    @property
    def TempComp(self):
        return self._tempComp

    @property
    def Temperature(self):
        return self._temperature
