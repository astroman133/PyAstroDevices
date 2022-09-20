import os
from os.path import exists
import json


class ApplicationSettings(object):
    """
    Provide access to the application settings file, including serialization
    to JSON and access to individual settings. The class is designed as a
    singleton class with access through the static GetInstance method.
    """

    _instance = None

    @staticmethod
    def GetInstance():
        """
        Provides access to the singleton instance, creating the instance if it
        does not already exist

        Returns the instance of ApplicationSettings
        """
        # Static Access Method

        if ApplicationSettings._instance is None:
            ApplicationSettings()

        return ApplicationSettings._instance

    def __init__(self):
        # the class instance initializer

        # prevent independent instantiation of the object

        if ApplicationSettings._instance is not None:
            raise Exception("The ApplicationSettings class is a singleton!")
        else:
            # save this instance and initialize the object with default values

            ApplicationSettings._instance = self
            self._windowLeft = 50
            self._windowTop = 50
            self._windowHeight = 470
            self._windowWidth = 420
            self._windowTitle = "ASCOM Device Control"
            self._telescopeAddress = "localhost:32323"
            self._telescopeDeviceNumber = 0
            self._telescopeDriverName = ""
            self._telescopeProtocol = "http"
            self._focuserAddress = "localhost:32323"
            self._focuserDeviceNumber = 0
            self._focuserDriverName = ""
            self._focuserProtocol = "http"

            self._InitGeometry()

    # Start of Public Methods and Properties

    @property
    def WindowLeft(self):
        return self._windowLeft

    @property
    def WindowTop(self):
        return self._windowTop

    @property
    def WindowHeight(self):
        return self._windowHeight

    @property
    def WindowWidth(self):
        return self._windowWidth

    @property
    def WindowTitle(self):
        return self._windowTitle

    @property
    def TelescopeAddress(self):
        return self._telescopeAddress

    @property
    def TelescopeDeviceNumber(self):
        return self._telescopeDeviceNumber

    @property
    def TelescopeDriverName(self):
        return self._telescopeDriverName

    @property
    def TelescopeProtocol(self):
        return self._telescopeProtocol

    @property
    def FocuserAddress(self):
        return self._focuserAddress

    @property
    def FocuserDeviceNumber(self):
        return self._focuserDeviceNumber

    @property
    def FocuserDriverName(self):
        return self._focuserDriverName

    @property
    def FocuserProtocol(self):
        return self._focuserProtocol

    def InitFromSettingsFile(self):
        """
        Read the contents of the settings file, deserialize the JSON and
        transfer the file's contents to the class's properties.
        """
        filename = os.environ["SETTINGS_FILE"]

        if exists(filename):
            # initialize the settings from the existing file

            f = open(filename)
            settings = json.load(f)

            self._windowLeft = settings["MAIN_WINDOW_LEFT"]
            self._windowTop = settings["MAIN_WINDOW_TOP"]
            self._windowHeight = settings["MAIN_WINDOW_HEIGHT"]
            self._windowWidth = settings["MAIN_WINDOW_WIDTH"]
            self._windowTitle = settings["MAIN_WINDOW_TITLE"]
            self._telescopeAddress = settings["TELESCOPE_ADDRESS"]
            self._telescopeDeviceNumber = settings["TELESCOPE_DEVICENUM"]
            self._telescopeDriverName = settings["TELESCOPE_DRIVER_NAME"]
            self._telescopeProtocol = settings["TELESCOPE_PROTOCOL"]
            self._focuserAddress = settings["FOCUSER_ADDRESS"]
            self._focuserDeviceNumber = settings["FOCUSER_DEVICENUM"]
            self._focuserDriverName = settings["FOCUSER_DRIVER_NAME"]
            self._focuserProtocol = settings["FOCUSER_PROTOCOL"]
            self._InitGeometry()

            f.close()

    def SetWindowSize(self, height, width):
        """
        Allows a user to update the settings with the size of the
        application's window.

        Positional arguments:
        height -- the height of the application's window
        width  -- the width of the application's window
        """
        self._windowHeight = height
        self._windowWidth = width

    def SetWindowPosition(self, left, top):
        """
        Allows a user to update the settings with the position of the
        application's window.

        Positional arguments:
        left -- the x-coordinate of the left side of the application's window.
        top  -- the y-coordinate of the top side of the application's window.
        """
        self._windowLeft = left
        self._windowTop = top

    def SetDeviceConfiguration(self, devType, devName, devAddr, devNumber, devProtocol):
        """
        Update the current settings instance with updated telescope or
        focuser configuration values

        Positional arguments:
        devType     -- either 'telescope' or 'focuser'
        devName     -- the name of the device
        devAddr     -- the device's IP address
        devNumber   -- the device number
        devProtocol -- either 'http' or 'https'
        """
        if devType.lower() == "telescope":
            self._telescopeDriverName = devName
            self._telescopeAddress = devAddr
            self._telescopeDeviceNumber = devNumber
            self._telescopeProtocol = devProtocol
        elif devType.lower() == "focuser":
            self._focuserDriverName = devName
            self._focuserAddress = devAddr
            self._focuserDeviceNumber = devNumber
            self._focuserProtocol = devProtocol

    def SaveSettings(self):
        """
        Save the current application settings to the settings file.
        """
        filename = os.environ["SETTINGS_FILE"]

        with open(filename, "w") as f:
            json.dump(
                self._ToJson(), f, indent=4, separators=(", ", ": "), sort_keys=True
            )

    # End of Public Methods and Properties

    # Start of Private Methods and Properties

    def _InitGeometry(self):
        # format the window size and position into a standard geometry string.

        self.Geometry = "%dx%d+%d+%d" % (
            self._windowWidth,
            self._windowHeight,
            self._windowLeft,
            self._windowTop,
        )

    def _ToJson(self):
        # format the current settings values into a JSON string that can be saved
        # to the settings file.

        return {
            "MAIN_WINDOW_LEFT": self._windowLeft,
            "MAIN_WINDOW_TOP": self._windowTop,
            "MAIN_WINDOW_HEIGHT": self._windowHeight,
            "MAIN_WINDOW_WIDTH": self._windowWidth,
            "MAIN_WINDOW_TITLE": self._windowTitle,
            "TELESCOPE_ADDRESS": self._telescopeAddress,
            "TELESCOPE_DEVICENUM": self._telescopeDeviceNumber,
            "TELESCOPE_DRIVER_NAME": self._telescopeDriverName,
            "TELESCOPE_PROTOCOL": self._telescopeProtocol,
            "FOCUSER_ADDRESS": self._focuserAddress,
            "FOCUSER_DEVICENUM": self._focuserDeviceNumber,
            "FOCUSER_DRIVER_NAME": self._focuserDriverName,
            "FOCUSER_PROTOCOL": self._focuserProtocol,
        }

    # End of Private Methods and Properties
