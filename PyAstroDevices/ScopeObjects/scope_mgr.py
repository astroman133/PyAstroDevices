import math
import copy
import threading as thread
from tkinter import messagebox

from pubsub import pub

from alpaca.telescope import *  # Multiple Classes including Enumerations
from alpaca.exceptions import *  # Or just the exceptions you want to catch

from scope_capabilities import TelescopeCapabilities
from scope_parameters import TelescopeParameters
from scope_status import TelescopeStatus
from scope_helpers import SlewDirection, NudgeDirection
from exception_formatter import ExceptionFormatter


class TelescopeManager:
    """
    This class manages communication with the selected telescope driver. All
    the views call through this class to issue commands to the driver. This
    class also handles periodic polling of the telescope.
    """

    _POLLING_INTERVAL_FAST = 1.0  # once per second
    _POLLING_INTERVAL_NORMAL = 5.0  # every 5 seconds
    _POLLING_INTERVAL_SLOW = 10.0  # every 10 seconds

    def __init__(self):
        # Initialize the instance level variables

        self._id = None
        self._telescope = None
        self._isConnected = False
        self._isPolling = False
        self._stopPolling = False
        self._pollingThread = None
        self._capabilities = None
        self._parameters = None
        self._connectError = None
        self._connectException = None

        self._SetSlewDirections()

    # Start of Public Properties

    @property
    def ID(self):
        return self._id

    @property
    def IsConnected(self):
        return self._isConnected

    @property
    def ConnectionError(self):
        return self._connectError

    @property
    def ConnectException(self):
        return self._connectException

    @property
    def Capabilities(self):
        return copy.copy(self._capabilities)

    @property
    def Parameters(self):
        return copy.copy(self._parameters)

    @property
    def SlewDirections(self):
        return copy.copy(self._slewDirections)

    # End of Public Properties

    # Start of Public Methods

    def Connect(self, address: str, deviceNumber: int, protocol: str = "http"):
        """
        Instantiate the telescope object and connect. Read the initial data
        from the driver and start polling for status updates

        Positional arguments:
        address      -- the internet address and port number of the Alpaca
                                        telescope driver
        deviceNumber -- the Alpaca device number
        protocol     -- the protocol; either 'http' or 'https'. 'http' is the
                                        default

        Returns - True if successfully connected, otherwise False
        """
        retval = False

        try:
            if self._telescope is None:
                self._telescope = Telescope(address, deviceNumber, protocol)
                # _id = (address, deviceNumber, protocol)
        except Exception as e:
            self._connectError = "Unable to create the telescope object."
            self._connectException = e
            return retval

        try:
            if not self._telescope.Connected:
                self._telescope.Connected = True

            self._isConnected = self._telescope.Connected
        except Exception as e:
            self._connectError = "Unable to connect to the telescope."
            self._connectException = e
            self._isConnected = False

            return retval

        possibleError = None

        try:
            if self.IsConnected:
                # read the capabilities from the telescope but be prepared
                # for an exception

                possibleError = "Unable to determine the telescope's "
                possibleError += "capabilities"
                self._capabilities = TelescopeCapabilities(self._telescope)
                pub.sendMessage("TelescopeCapabilitiesUpdate", caps=self._capabilities)

                possibleError = "Unable to determine the telescope's "
                possibleError += "configuration parameters"
                self._parameters = TelescopeParameters(self._telescope)

                # set the slew directions as soon as we know the alignment mode
                # so that subscribers to the parameters update msg can
                # get them.

                possibleError = "Unable to set the slew directions"
                self._SetSlewDirections()

                pub.sendMessage("TelescopeParametersUpdate", parms=self._parameters)

                possibleError = "Unable to start the device polling."
                self._StartDevicePolling()
        except Exception as e:
            self._connectError = possibleError
            self._connectException = e

            return retval

        if self._telescope is not None:
            retval = self._isConnected

        return retval

    def Disconnect(self):
        """
        This method stops the polling thread, sets the scope's Connected
        property to False, initializes the Parameters, Capabilities, and
        Status objects to their initialized state and sends them to any
        subscribers (the views).
        """
        if self._telescope is None:
            msg = "TelescopeManager.Disconnect() was called when no Telescope "
            msg += "has been created."
            raise InvalidOperationException(msg)

        if self._pollingThread is not None:
            self._stopPolling = True
            self._InterruptPollingSleep()
            self._pollingThread.join()

        self._telescope.Connected = False
        self._isConnected = False
        self._telescope = None

        self._status = TelescopeStatus()
        pub.sendMessage("TelescopeStatusUpdate", sts=self._status)

        self._capabilities = TelescopeCapabilities()
        pub.sendMessage("TelescopeCapabilitiesUpdate", caps=self._capabilities)

        self._parameters = TelescopeParameters()
        self._SetSlewDirections()
        pub.sendMessage("TelescopeParametersUpdate", parms=self._parameters)
 
    def ImmediateStatusUpdate(self):
        """
        Wake the polling loop to cause an immediate status update to occur.
        """
        if self._telescope is not None and self._isConnected:
            self._InterruptPollingSleep()

    def SetTracking(self, tracking):
        """
        Turn tracking on or off

        Positional arguments:
        tracking -- the requested state of the driver's tracking flag
        """
        if self._telescope is not None and self._isConnected:
            if tracking != self._telescope.Tracking:
                self._telescope.Tracking = tracking
                self._InterruptPollingSleep()

    def SlewToPark(self):
        """
        Park the telescope
        """
        if self._telescope is not None and self._isConnected:
            if self._telescope.Slewing:
                msg = "TelescopeManager.SlewToPark was called when the "
                msg += "telescope was already slewing."
                raise InvalidOperationException(msg)
            self._telescope.Park()
            self._InterruptPollingSleep()

    def SetUnparkedState(self):
        """
        Unpark the telescope
        """
        if self._telescope is not None and self._isConnected:
            if self._capabilities.CanUnpark:
                self._telescope.Unpark()
                self._InterruptPollingSleep()  # force status update

    def GetTrackingRate(self):
        """
        Get the current tracking rate

        Return value -- the current rate (one of the driver's TrackingRates)
        """
        retval = DriveRates.DriveSidereal

        if self._telescope is not None and self._isConnected:
            try:
                retval = self._telescope.TrackingRate
            except Exception:
                pass

        return retval

    def SetTrackingRate(self, trackingRate):
        """
        Set the current tracking rate

        Positional arguments:
        trackingRate -- the requested tracking rate
        """
        if self._telescope is not None and self._isConnected:
            self._telescope.TrackingRate = trackingRate
            self._InterruptPollingSleep()

    def GetRaOffsetTrackingRate(self):
        """
        Get the current RightAscensionRate of the telescope

        Returns -- the right ascension offset rate
        """
        retval = float("nan")

        if self._telescope is not None and self._isConnected:
            retval = self._telescope.RightAscensionRate

        return retval

    def GetDecOffsetTrackingRate(self):
        """
        Get the current DeclinationRate of the telescope

        returns -- the declination offset rate
        """
        retval = float("nan")

        if self._telescope is not None and self._isConnected:
            retval = self._telescope.DeclinationRate

        return retval

    def SetOffsetTrackingRates(self, raRate, decRate):
        """
        Set the current RA and Dec tracking rate offsets

        Positional arguments:
        raRate  -- the right ascension tracking rate offset. The units are
                                seconds of RA per sidereal second.
        decRate -- the declination tracking rate offset. The units are
                                arc-seconds per SI second.
        """
        forceUpdate = False
        if self._telescope is not None and self._isConnected:
            if self._capabilities.CanSetRightAscensionRate:
                self._telescope.RightAscensionRate = raRate
                forceUpdate = True

            if self._capabilities.CanSetDeclinationRate:
                self._telescope.DeclinationRate = decRate
                forceUpdate = True

        if forceUpdate:
            self.ImmediateStatusUpdate()

    def StartNudgeScope(self, direction, rate):
        """
        Start a nudge operation

        Positional arguments:
        direction -- the nudge direction (member of the NudgeRates
                                enumeration)
        rate	  -- the requested nudge rate, in degrees per second
        """
        if self._telescope is None or not self._isConnected:
            msg = "TelescopeManager.StartNudgeScope() was called when no "
            msg += "Telescope is connected."
            raise InvalidOperationException(msg)

        if self._telescope.Slewing:
            msg = "TelescopeManager is unable to call MoveAxis() when the "
            msg = "telescope is slewing"
            raise InvalidOperationException(msg)

        if self._telescope.CanMoveAxis(
            TelescopeAxes.axisPrimary
        ) and self._telescope.CanMoveAxis(TelescopeAxes.axisSecondary):
            self._StartNudgeMoveAxis(direction, rate)
        else:
            msg = "The telescope does not support MoveAxis for the primary "
            msg += "and secondary axes."
            raise InvalidOperationException(msg)

    def StopNudgeScope(self, direction):
        """
        Stop nudging the scope in the requested direction

        Positional arguments:
        direction -- the requested direction to stop nudging
        """
        if self._telescope is None or not self._isConnected:
            msg = "TelescopeManager.StopNudgeScope() was called when no "
            msg += "Telescope is connected."
            raise InvalidOperationException(msg)

        if self._telescope.CanMoveAxis(
            TelescopeAxes.axisPrimary
        ) and self._telescope.CanMoveAxis(TelescopeAxes.axisSecondary):
            self._StopNudgeMoveAxis(direction)

    def SlewToCoordinatesAsync(self, ra, dec):
        """
        Perform an asynchronous slew to the requested equatorial coordinates

        Positional arguments:
        ra  -- the destination right ascension
        dec -- the destination declination
        """
        if self._telescope is not None and self._isConnected:
            if self._telescope.Slewing:
                msg = "TelescopeManager.SlewToCoordinatesAsync cannot begin a "
                msg += "slew while the telescope is already slewing."
                raise InvalidOperationException(msg)

            self._telescope.SlewToCoordinatesAsync(ra, dec)
            self.ImmediateStatusUpdate()

    def SlewToAltAzAsync(self, az, alt):
        """
        Perform an asynchronous slew to the requested terrestrial coordinates

        Positional arguments:
        az  -- the destination azimuth
        alt -- the destination altitude
        """
        if self._telescope is not None and self._isConnected:
            if self._telescope.Slewing:
                msg = "TelescopeManager.SlewToAltAzAsync cannot begin a slew "
                msg += "while the telescope is already slewing."
                raise InvalidOperationException(msg)

            self._telescope.SlewToAltAzAsync(az, alt)
            self.ImmediateStatusUpdate()

    def AbortSlew(self):
        """
        Abort any asynchronous slew and resume tracking, if enabled
        """
        if self._telescope is None or not self._isConnected:
            return

        if self._telescope.Slewing:
            self._telescope.AbortSlew()

    def StartMeridianFlip(self):
        """
        Flip a GEM to the other side of the meridian, if in a counterweight
        up state
        """
        if self._telescope is None or not self._isConnected:
            if self._telescope.Slewing:
                msg = "TelescopeManager.StartMeridianFlip cannot begin a "
                msg += "slew while the telescope is already slewing."
                raise InvalidOperationException(msg)

        if self._parameters.AlignmentMode != AlignmentModes.algGermanPolar:
            msg = "TelescopeManager.StartMeridianFlip cannot flip a "
            msg += "mount that is not a German Equatorial mount."
            raise InvalidOperationException(msg)

        if self._capabilities.CanSetPierSide:
            # Change the Side of the Pier

            currentSide = self._telescope.SideOfPier
            newSide = PierSide.pierUnknown

            if currentSide.value == PierSide["pierEast"].value:
                newSide = PierSide.pierWest
            elif currentSide.value == PierSide["pierWest"].value:
                newSide = PierSide.pierEast

            if newSide != PierSide.pierUnknown:
                self._telescope.SideOfPier = newSide
        else:
            # Slew to the same coordinates to do the flip

            ra = self._telescope.RightAscension
            dec = self._telescope.Declination

            self._telescope.SlewToCoordinatesAsync(ra, dec)

    def SetParkPosition(self):
        """
        Set the current altitude and azimuth as the current park position.
        """
        self._telescope.SetPark()

    def ChangeTrackingState(self, newState):
        """
        Set the telescope's tracking state

        Positional arguments:
        newState -- the target tracking state, True or False
        """
        self._telescope.Tracking = newState
        self._InterruptPollingSleep()

    def SeekHomePosition(self):
        """
        Slew to the telescope's Home position
        """
        if self._capabilities.CanFindHome:
            self._telescope.FindHome()

    # End of Public Methods

    # Private Helper Methods

    def _GetNudgeAxis(self, direction):
        # translate a nudge direction into the corresponding axis

        if direction == NudgeDirection.Nothing:
            return None

        retval = TelescopeAxes.axisPrimary

        if direction.value in (
            NudgeDirection["North"].value,
            NudgeDirection["South"].value,
        ):
            retval = TelescopeAxes.axisSecondary

        return retval

    def _ValidateMoveAxisRate(self, axis, rate):
        # validate the passed axis and rate against the driver's axis rates

        retval = False

        # Check the requsted rate against the valid rates

        if axis == TelescopeAxes.axisPrimary:
            axisRates = self.Capabilities.PrimaryAxisRates
        else:
            axisRates = self.Capabilities.SecondaryAxisRates

        count = len(axisRates)
        tolerance = 0.00001

        for i in range(count):
            axisRate = axisRates[i]
            minimum = axisRate.Minimum - tolerance
            maximum = axisRate.Maximum + tolerance

            if rate >= minimum and rate <= maximum:
                retval = True
                break

        if not retval:
            # invalid rate throw an exception

            msg = "The requested move rate is invalid.\r\n\r\n"
            msg += "A valid rate must be in one of the following ranges:"

            for i in range(count):
                rate = axisRates[i]
                msg += f"{rate.Minimum} - {rate.Maximum}\r\n"

            raise Exception("msg")

        return retval

    def _GetNudgeSign(self, direction):
        # get the sign of the move for a given direction

        retval = 1.0

        if direction.value in (
            NudgeDirection["South"].value,
            NudgeDirection["East"].value,
        ):
            retval = -1.0

        return retval

    def _StartNudgeMoveAxis(self, direction, rate):
        # start nudging the scope at the requested rate, in the requested
        # direction

        axis = self._GetNudgeAxis(direction)

        if axis is None:
            msg = "TelescopeManager.StartNudgeMoveAxis called with an "
            msg += "invalid direction"
            raise InvalidValueException(msg)

        self._ValidateMoveAxisRate(axis, rate)
        trueRate = rate * self._GetNudgeSign(direction)

        self._telescope.MoveAxis(axis, trueRate)
        self._InterruptPollingSleep()

    def _StopNudgeMoveAxis(self, direction):
        # stop nudging the scope in the requested direction

        if self._telescope is None or not self._isConnected:
            msg = "TelescopeManager.StopNudgeScope() was called when no "
            msg += "Telescope is connected."
            raise InvalidOperationException(msg)

        if direction == NudgeDirection.Nothing:
            # here stop both axes from moving

            if self._telescope.CanMoveAxis(TelescopeAxes.axisPrimary):
                self._telescope.MoveAxis(TelescopeAxes.axisPrimary, 0.0)

            if self._telescope.CanMoveAxis(TelescopeAxes.axisSecondary):
                self._telescope.MoveAxis(TelescopeAxes.axisSecondary, 0.0)
        else:
            axis = self._GetNudgeAxis(direction)
            self._telescope.MoveAxis(axis, 0.0)

    def _SetSlewDirections(self):
        # set the slew directions based on the driver's AlignmentMode
        #  property.

        self._slewDirections = []

        self._slewDirections.append(SlewDirection("N", "North"))
        self._slewDirections.append(SlewDirection("S", "South"))
        self._slewDirections.append(SlewDirection("W", "West"))
        self._slewDirections.append(SlewDirection("E", "East"))

        if self._telescope is not None:
            if self._parameters.AlignmentMode == AlignmentModes.algAltAz:
                self._slewDirections.clear()
                self._slewDirections.append(SlewDirection("U", "Up"))
                self._slewDirections.append(SlewDirection("D", "Down"))
                self._slewDirections.append(SlewDirection("L", "Left"))
                self._slewDirections.append(SlewDirection("R", "Right"))
            elif self._parameters.SiteLatitude < 0:
                self._slewDirections.clear()
                self._slewDirections.append(SlewDirection("S", "South"))
                self._slewDirections.append(SlewDirection("N", "North"))
                self._slewDirections.append(SlewDirection("W", "West"))
                self._slewDirections.append(SlewDirection("E", "East"))

    def _PollScopeTask(self, stop):
        # this method runs on a worker thread to periodically read and update
        # the current telescope status

        while True:
            if stop():  # terminate and return
                break

            # get fresh status from the telescope

            try:
                self._status = TelescopeStatus(self._telescope)
            except Exception as xcp:
                self._pollingException = xcp

                pub.sendMessage("TelescopePollingException", xcp=xcp)

                return

            # send status update message

            pub.sendMessage("TelescopeStatusUpdate", sts=self._status)

            # set our sleep interval to normal or fast (if slewing)

            interval = self._POLLING_INTERVAL_NORMAL

            if self._status.Slewing:
                interval = self._POLLING_INTERVAL_FAST

            # wait until we are signaled or until the sleep interval has
            # expired.

            flag = self._eventObj.wait(interval)

            # reset the event object so we can reuse it.

            if flag:
                self._eventObj.clear()

    def _StartDevicePolling(self):
        # begin polling any connected telescope for fresh status

        # return if no connected scope

        if self._telescope is None or not self._isConnected:
            return
        # return if already polling the scope

        if self._isPolling:
            return

        # subscribe to receive any unhandled exception raised by the polling
        # thread.

        pub.subscribe(self._PollingExceptionListener, "TelescopePollingException")

        # create a worker thread to poll the telescope

        self._eventObj = thread.Event()
        self._stopPolling = False
        self._pollingThread = thread.Thread(
            target=self._PollScopeTask, args=(lambda: self._stopPolling,)
        )
        self._pollingThread.start()

    def _InterruptPollingSleep(self):
        # interrupt the polling thread to force an immediate status update or
        # to cause the thread to exit
        self._eventObj.set()

    def _PollingExceptionListener(self, xcp):
        # Stop the polling loop in response to an error and report the error
        # to the user.

        msg = "An error occurred while reading data from the telescope. The "
        msg += "error is fatal and the telescope must be disconnected. "
        msg += "Details follow:\r\n\r\n"
        formatter = ExceptionFormatter.GetInstance()
        msg += formatter.Format(xcp)
        messagebox.showerror("Slewing Error Occurred", msg)

        self._stopPolling = True
        self._InterruptPollingSleep()
        self.pollingThread.join()
        self._pollingThread = None
        self.Disconnect()

    # End of Private Helper Methods
