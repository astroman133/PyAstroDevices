import copy
import threading as thread
from tkinter import messagebox

from pubsub import pub

from alpaca.focuser import *
from alpaca.exceptions import *

from focuser_parameters import FocuserParameters
from focuser_status import FocuserStatus
from exception_formatter import ExceptionFormatter


class FocuserManager:
    """
    This class manages communication with the selected focuser driver. All the
    views call through this class to issue commands to the driver. This class
	also handles periodic polling of the focuser.
	"""

    _POLLING_INTERVAL_FAST = 1.0  # once per second
    _POLLING_INTERVAL_NORMAL = 5.0  # every 5 seconds
    _POLLING_INTERVAL_SLOW = 10.0  # every 10 seconds

    def __init__(self):
        # Initialize the instance level variables

        self._status = FocuserStatus()
        self._id = None
        self._focuser = None
        self._isConnected = False
        self._isPolling = False
        self._stopPolling = False
        self._pollingThread = None
        self._capabilities = None
        self._parameters = None
        self._connectError = None
        self._connectException = None
        self._reenableTempComp = False

    # Public Properties

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

    # End of Public Properties

    # Start of Public Methods

    def Connect(self, address: str, deviceNumber: int, protocol: str = 'http'):
        """
        Instantiate the focuser object and connect. Read the initial data from
        the driver and start polling for status updates

        Positional arguments:
        address      -- the internet address and port number of the focuser driver
        deviceNumber -- the Alpaca device number
        protocol     -- the protocol; either 'http' or 'https'

        Returns - True if successfully connected, otherwise False
        """
        retval = False

        try:
            if self._focuser is None:
                self._focuser = Focuser(address, deviceNumber, protocol)
        except Exception as e:
            self._connectError = "Unable to create the focuser object."
            self._connectException = e
            return retval

        try:
            if not self._focuser.Connected:
                self._focuser.Connected = True

            self._isConnected = self._focuser.Connected
        except Exception as e:
            self._connectError = "Unable to connect to the focuser."
            self._connectException = e
            self._isConnected = False

            return retval

        possibleError = None

        try:
            if self.IsConnected:
                possibleError = "Unable to determine the focuser's"
                possibleError += ' configuration parameters'
                self._parameters = FocuserParameters(self._focuser)
                pub.sendMessage('FocuserParametersUpdate'
                                , parms=self._parameters)

                possibleError = 'Unable to get the focuser\'s status.'
                pub.sendMessage('FocuserStatusUpdate', sts=self._status)

                possibleError = "Unable to start the device polling.";
                self._StartDevicePolling();
        except Exception as e:
            self._connectError = possibleError
            self._connectException = e

            return retval

        if self._focuser is not None:
            retval = self._isConnected

        return retval

    def Disconnect(self):
        """
		This method stops the polling thread, sets the focuser's Connected
		property to False, initializes the Parameters and Status objects to
		their initialized state and sends them to any subscribers (the views).
		"""
        if (self._focuser is None):
            msg = 'FocuserManager.Disconnect() was '
            msg += 'called when no Focuser has been created.'

            raise InvalidOperationException(msg)

        if (self._pollingThread is not None):
            self._stopPolling = True  # Terminate the polling thread
            self._InterruptPollingSleep()  # Wake up the polling thread
            self._pollingThread.join()  # Block until the polling thread is
        #  terminated

        # disconnect the focuser and release the driver
        self._focuser.Connected = False
        self._isConnected = False
        self._focuser = None

        # initialize the status and parameters objects
        pub.sendMessage('FocuserStatusUpdate', sts=self._status)
        self._parameters = FocuserParameters()
        pub.sendMessage('FocuserParametersUpdate', parms=self._parameters)

    def ImmediateStatusUpdate(self):
        """
		This method interrupts the polling sleep cycle to allow the status 
		update to occur immediately.
		"""
        if (self._focuser is not None and self._isConnected):
            self._InterruptPollingSleep()

    def MoveFocuserBy(self, amount):
        """
		Move the focuser by the specified amount.
		If the focuser is an absolute focuser, the move amount is added to the 
		current position to determine the new target position.

		The value to be sent to the driver is clammped to prevent trying to move
		the focuser too much or too far in a single move.

		If necessary temperature compensation is temporarily disabled while the
		focuser is being moved.

		Positional arguments:
		amount  -- the number of steps requested to be moved
		"""
        maxIncrement = self._parameters.MaxIncrement
        maxStep = self._parameters.MaxStep
        interfaceVersion = self._parameters.InterfaceVersion
        tempCompOn = self._status.TempComp

        # ensure that our move amount does not exceed the MaxIncrement

        moveValue = self._Clamp(amount, -maxIncrement, maxIncrement)

        # notify the view about how much we are moving to support keeping track
        # of accumulated moves.

        pub.sendMessage('FocuserMoveUpdate', amount=moveValue)

        if (self._parameters.Absolute):
            moveValue += self._status.Position

            # make sure that we do not exceed the maximum allowable position
            # (either + or -).

            moveValue = self._Clamp(moveValue, -maxStep, maxStep)

        # if the driver is earlier than IFocuserV3 and temp comp is on then we
        # need to disable it prior to the move

        if (interfaceVersion < 3 and tempCompOn):
            self._focuser.TempComp = False
            self._reenableTempComp = True

        # move the focuser. If the focuser is absolute, moveValue is the target
        # position. If the focuser is not absolute, then move value is the steps
        # to move.

        self._focuser.Move(moveValue)
        self.ImmediateStatusUpdate()

    def HaltFocuser(self):
        """
		Immediately abort focuser movement.
		"""
        if (self._focuser.IsMoving):
            self._focuser.Halt()
            self.ImmediateStatusUpdate()
            pub.sendMessage('FocuserMoveCompleted')

    def SetTemperatureCompensation(self, state):
        """
		Turn temperature compensation on or off

		Positional arguments:
		state -- True, if temperature compensation is to be activated, 
						otherwise False
		"""
        if (self._parameters.TempCompAvailable):
            self._focuser.TempComp = state
            self.ImmediateStatusUpdate()

    # End of Public Methods

    # Start of Private Helper Methods

    def _PollFocuserTask(self, stop):
        # This method runs on a worker thread, until it is stopped.
        # Every trip through the main processing loop it updates the
        # focuser status and sends the fresh status to message subscribers.
        # When finished with the status updates it goes to sleep to wait for
        # the next cycle. It can be signaled to wake up, as needed to perform
        # immediate status updates. It also sleeps for a shorter interval when
        # the focuser is moving

        # The stop argument is an anonymous method provided by the caller that
        # is used to signal us to end the thread.
        while True:
            if (stop()):  # terminate and return
                break

            # get fresh status from the focuser

            try:
                self._status = FocuserStatus(self._focuser)
            except Exception as xcp:
                self._pollingException = xcp

                pub.sendMessage('FocuserPollingException', xcp=xcp)

                return

            # send status update message

            pub.sendMessage('FocuserStatusUpdate', sts=self._status)

            # set our sleep interval to normal or fast (if slewing)

            interval = self._POLLING_INTERVAL_NORMAL

            if (self._status.IsMoving):
                interval = self._POLLING_INTERVAL_FAST

            # wait until we are signaled or until the sleep interval has expired.

            flag = self._eventObj.wait(interval)

            # reset the event object so we can reuse it.

            if (flag):
                self._eventObj.clear()

    def _StartDevicePolling(self):
        # Starts the polling thread

        # return if no connected focuser

        if (self._focuser is None or not self._isConnected):
            return

        # return if already polling the focuser

        if (self._isPolling):
            return

        # subscribe to receive any unhandled exception raised by the
        # polling thread

        pub.subscribe(self._MovingExceptionListener, 'FocuserMovingException')

        # create a worker thread to poll the focuser

        self._eventObj = thread.Event()
        self._stopPolling = False
        self._pollingThread = thread.Thread(target=self._PollFocuserTask
                                            , args=(lambda: self._stopPolling,))
        self._pollingThread.start()

    def _InterruptPollingSleep(self):
        # Cause the polling cycle to wake immediately
        self._eventObj.set()

    def _MovingExceptionListener(self, xcp):
        # Stop the polling loop in response to an error and report the error
        # to the user.

        msg = 'An error occurred while reading data from the focuser. '
        msg += 'The error is fatal and the focuser must be disconnected. '
        msg += 'Details follow:\r\n\r\n'
        formatter = ExceptionFormatter.GetInstance()
        msg += formatter.Format(xcp)
        messagebox.showerror("Moving Error Occurred", msg)

        self._stopPolling = True
        self._InterruptPollingSleep()
        self.pollingThread.join()
        self._pollingThread = None
        self.Disconnect()

    def _Clamp(self, amount, minValue, maxValue):
        # Clamp the specified amount between the min and max values, if
        # necessary.

        clamped = amount

        if (amount < minValue):
            clamped = minValue
        elif (amount > maxValue):
            clamped = maxValue

        return clamped

# End of Private Helper Methods
