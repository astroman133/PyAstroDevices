from alpaca.focuser import *


class FocuserParameters:
    """
    Class to contain properties that are read from the focuser and not changed
    by the application. The initializer has the abilty to create an empty
    instance, or one with values read from the driver.
    """

    def __init__(self, focuser=None):
        # Initialize the object instance

        self._focuser = focuser

        if focuser:
            # populate this instance with values read from the focuser driver

            self._absolute = focuser.Absolute
            self._description = focuser.Description
            self._driverInfo = focuser.DriverInfo
            self._driverVersion = focuser.DriverVersion
            self._interfaceVersion = focuser.InterfaceVersion
            self._maxIncrement = focuser.MaxIncrement
            self._maxStep = focuser.MaxStep
            self._stepSize = focuser.StepSize
            self._tempCompAvailable = focuser.TempCompAvailable
        else:
            # create an instance populated with initial/default values

            self._absolute = True
            self._description = ""
            self._driverInfo = ""
            self._driverVersion = ""
            self._interfaceVersion = 0
            self._maxIncrement = 0
            self._maxStep = 0
            self._stepSize = 0
            self._tempCompAvailable = False

    @property
    def Absolute(self):
        return self._absolute

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
    def InterfaceVersion(self):
        return self._interfaceVersion

    @property
    def IsConnected(self):
        return False if (self._focuser is None) else True

    @property
    def MaxIncrement(self):
        return self._maxIncrement

    @property
    def MaxStep(self):
        return self._maxStep

    @property
    def StepSize(self):
        return self._stepSize

    @property
    def TempCompAvailable(self):
        return self._tempCompAvailable
