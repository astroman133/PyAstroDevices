import locale
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from tkinter import messagebox

from PIL import Image, ImageTk
from pubsub import pub
from alpaca.focuser import *  # Multiple Classes including Enumerations

from exception_formatter import ExceptionFormatter
from focuser_status import FocuserStatus
from integer_entry_widget import IntegerEntry


class FocuserControlView:
    """
    This class manages the display and interaction of the widgets on the
    Focuser Control tab page
    """

    _ERROR_TITLE = "Focuser Driver Error"

    def __init__(self, parentFrame, focuserManager):
        # object instance initializer

        self._parent = parentFrame
        self._mgr = focuserManager
        self._status = None

        # create the variables that will be bound to the U/I

        nd = "NO DATA"
        self._isConnectedDisplay = tk.StringVar(master=None)
        self._isConnectedDisplay.set("Not Connected")
        self._positionDisplay = tk.StringVar(master=None)
        self._positionDisplay.set(nd)
        self._temperatureDisplay = tk.StringVar(master=None)
        self._temperatureDisplay.set(nd)
        self._temperatureUnitsDisplay = tk.StringVar(master=None)
        self._temperatureUnitsDisplay.set("F")
        self._tempCompDisplay = tk.IntVar(master=None)
        self._tempCompDisplay.set(0)
        self._moveAmountDisplay = tk.DoubleVar(master=None)
        self._moveAmountDisplay.set(6)
        self._accumulatedTotalSteps = tk.IntVar(master=None)
        self._accumulatedTotalSteps.set(0)
        self._moveToAmountDisplay = tk.IntVar(master=None)
        self._moveToAmountDisplay.set(0)
        self._movementStatusDisplay = tk.StringVar(master=None)
        self._movementStatusDisplay.set(nd)

        self._moveAmount = 1000

        pub.subscribe(self._ParmsListener, "FocuserParametersUpdate")
        pub.subscribe(self._StatusListener, "FocuserStatusUpdate")
        pub.subscribe(self._MoveAmountListener, "FocuserMoveUpdate")
        pub.subscribe(self._DisconnectListener, "FocuserDisconnect")

        self._CreateWidgets()

    # Start of Public Properties and Methods

    # End of Public Properties and Methods

    # Start of Private Properties and Methods

    def _CreateWidgets(self):
        # create the style to display labels in red

        lblStyle = ttk.Style()
        lblStyle.configure("ValueText.TLabel", foreground="red")

        # create the widgets on the Focuser Control tab page

        controlFrame = tk.Frame(self._parent)
        controlFrame.grid_rowconfigure(0, weight=1)
        controlFrame.grid_rowconfigure(1, weight=1)
        controlFrame.grid_rowconfigure(2, weight=1)
        controlFrame.grid_rowconfigure(3, weight=1)
        controlFrame.grid_rowconfigure(4, weight=1)
        controlFrame.grid_rowconfigure(5, weight=1)
        controlFrame.grid_rowconfigure(6, weight=1)
        controlFrame.grid_rowconfigure(7, weight=1)
        controlFrame.grid_columnconfigure(0, weight=1)

        # connected status label

        isConnectedLabel = ttk.Label(
            controlFrame,
            textvariable=self._isConnectedDisplay,
            style="ValueText.TLabel",
            font=("Arial", 12),
        )
        isConnectedLabel.grid(row=0, column=0)

        # current position, label, and value

        positionFrame = tk.Frame(controlFrame)
        lbl = ttk.Label(positionFrame, text="Position:", font=("Arial", 12))
        lbl.pack(side=tk.LEFT)
        positionValue = ttk.Label(
            positionFrame,
            textvariable=self._positionDisplay,
            style="ValueText.TLabel",
            font=("Arial", 12),
        )
        positionValue.pack(side=tk.LEFT, padx=4)
        positionFrame.grid(row=1, column=0)

        # current temperature label, value, and units

        temperatureFrame = tk.Frame(controlFrame)
        lbl = ttk.Label(temperatureFrame, text="Temperature:", font=("Arial", 12))
        lbl.pack(side=tk.LEFT)
        lbl = ttk.Label(
            temperatureFrame,
            textvariable=self._temperatureDisplay,
            style="ValueText.TLabel",
            width=8,
            font=("Arial", 12),
        )
        lbl.pack(side=tk.LEFT, padx=(4, 20))

        # temperature units radio buttons

        rbStyle = ttk.Style()
        rbStyle.configure("my.TRadiobutton", font=("Arial", 12))
        #units = "\N{DEGREE SIGN}" + "F"
        units = chr(176) + 'F'
        self._useDegFRadioBtn = ttk.Radiobutton(
            temperatureFrame,
            text=units,
            value="F",
            variable=self._temperatureUnitsDisplay,
            command=self._OnUnitsChanged,
            style="my.TRadiobutton",
        )
        self._useDegFRadioBtn.pack(side=tk.LEFT)

        #units = "\N{DEGREE SIGN}" + "C"
        units = chr(176) + 'C'
        rb2 = ttk.Radiobutton(
            temperatureFrame,
            text=units,
            value="C",
            variable=self._temperatureUnitsDisplay,
            command=self._OnUnitsChanged,
            style="my.TRadiobutton",
        )
        rb2.pack(side=tk.LEFT, padx=4)

        temperatureFrame.grid(row=2, column=0)

        # temperature compensatiuon checkbox

        cbStyle = ttk.Style()
        cbStyle.configure("my.TCheckbutton", font=("Arial", 12))
        tempCompCheckbtn = ttk.Checkbutton(
            controlFrame,
            text="TemperatureCompensation",
            style="my.TCheckbutton",
            variable=self._tempCompDisplay,
            command=self._OnTempCompStateChanged,
        )
        tempCompCheckbtn.grid(row=3, column=0)

        # move amount buttons

        moveAmountFrame = tk.Frame(controlFrame)
        moveAmountFrame.grid_rowconfigure(0)
        moveAmountFrame.grid_rowconfigure(1)
        moveAmountFrame.grid_columnconfigure(0)
        moveAmountFrame.grid_columnconfigure(0)
        lblStyle = ttk.Style()
        lblStyle.configure("my.TLabel", font=("Arial", 9))
        moveAmountLbl = ttk.Label(
            moveAmountFrame, text="Select the move amount:", style="my.TLabel"
        )
        moveAmountLbl.grid(row=0, column=0, padx=3)

        # move amount slider

        scale = tk.Scale(
            moveAmountFrame,
            orient=tk.HORIZONTAL,
            from_=0,
            to=6,
            showvalue=0,
            variable=self._moveAmountDisplay,
            length=180,
            tickinterval=0,
            command=self._OnMoveAmountChanged,
        )
        scale.grid(row=0, column=1)
        self._moveAmtLabel = ttk.Label(moveAmountFrame, text="1000 steps/move")
        self._moveAmtLabel.grid(row=1, column=1)

        moveAmountFrame.grid(row=4, column=0)

        buttonFrame = tk.Frame(controlFrame)
        buttonFrame.grid_rowconfigure(0)
        buttonFrame.grid_columnconfigure(0)
        buttonFrame.grid_columnconfigure(1)
        buttonFrame.grid_columnconfigure(2)
        buttonFrame.grid_columnconfigure(3)
        buttonFrame.grid_columnconfigure(4)
        buttonFrame.grid_columnconfigure(5)

        # font for rectangular button labels

        font = tkFont.Font(family="Arial", size=10)
        bsize = 35  # pixel size of square buttons

        # create a blank image to allow the buttons to be measured in pixels

        self._blankImage = tk.PhotoImage()

        # create and configure the Move In button

        btemp = tk.Button(
            buttonFrame,
            text="Move\nIn",
            image=self._blankImage,
            state="disabled",
            font=font,
            compound=tk.CENTER,
            command=self._OnMoveInClick,
        )
        btemp.config(height=bsize, width=bsize)
        btemp.grid(row=0, column=0, sticky="NWSE", padx=4, pady=12)
        self._moveInBtn = btemp

        # create and configure the abort move button

        image = Image.open("./assets/stop.png")
        image = image.resize((33, 33), Image.ANTIALIAS)
        self._stopIcon = ImageTk.PhotoImage(image)
        btemp = tk.Button(
            buttonFrame,
            text=None,
            image=self._stopIcon,
            state="disabled",
            width=0,
            compound=tk.CENTER,
            command=self._OnAbortMoveClick,
        )
        btemp.config(height=bsize, width=bsize)
        btemp.grid(row=0, column=1, sticky="NWSE", padx=4, pady=12)
        self._abortMoveBtn = btemp

        # create and configure the Move Out button

        btemp = tk.Button(
            buttonFrame,
            text="Move\nOut",
            image=self._blankImage,
            state="disabled",
            font=font,
            compound=tk.CENTER,
            command=self._OnMoveOutClick,
        )
        btemp.config(height=bsize, width=bsize)
        btemp.grid(row=0, column=2, sticky="NWSE", padx=4, pady=12)
        self._moveOutBtn = btemp

        # create the group box to contain the accumulated total steps widgets

        totalSteps = ttk.LabelFrame(buttonFrame, text="Accumulated Total Steps")
        self._stepEntry = IntegerEntry(
            totalSteps,
            width=10,
            state="readonly",
            textvariable=self._accumulatedTotalSteps,
        )
        self._stepEntry.pack(side=tk.LEFT, padx=6, pady=4)

        self._editTotalStepsBtn = ttk.Button(
            totalSteps,
            text="Edit",
            width=5,
            state="disabled",
            command=self._OnEditStepsClick,
        )
        self._editTotalStepsBtn.pack(side=tk.LEFT, padx=6, pady=4)
        self._resetTotalStepsBtn = ttk.Button(
            totalSteps,
            text="Reset",
            width=5,
            state="disabled",
            command=self._OnResetStepsClick,
        )
        self._resetTotalStepsBtn.pack(side=tk.LEFT, padx=6, pady=4)

        totalSteps.grid(row=0, column=3, columnspan=3, padx=4)
        buttonFrame.grid(row=5, column=0, sticky="w")

        # create the target position and the absolute move button

        moveToFrame = tk.Frame(controlFrame)
        ttk.Label(moveToFrame, text="Move To Position:").pack(side=tk.LEFT, padx=4)

        self._moveToPositionEntry = IntegerEntry(
            moveToFrame,
            width=8,
            state="disabled",
            textvariable=self._moveToAmountDisplay,
        )
        self._moveToPositionEntry.pack(side=tk.LEFT, padx=4)

        self._moveToPositionBtn = ttk.Button(
            moveToFrame,
            text="Go",
            width=4,
            command=self._OnMoveToBtnClick,
            state="disabled",
        )
        self._moveToPositionBtn.pack(side=tk.LEFT, padx=4)
        moveToFrame.grid(row=6, column=0, sticky="w")

        # create the movement status widgets and add them to the grid

        moveStatusFrame = tk.Frame(controlFrame)
        lbl = ttk.Label(moveStatusFrame, text="Movement Status:", font=("Arial", 12))
        lbl.pack(side=tk.LEFT)

        stateValue = ttk.Label(
            moveStatusFrame,
            textvariable=self._movementStatusDisplay,
            style="ValueText.TLabel",
            font=("Arial", 12),
        )
        stateValue.pack(side=tk.LEFT, padx=(4, 0))

        moveStatusFrame.grid(row=7, column=0, pady=(4, 0))

        # position the control frame

        controlFrame.grid(row=0, column=0, padx=20)

    def _OnMoveInClick(self):
        # click handler for the Move In button

        self._RequestFocuserMove(-self._moveAmount)

    def _OnMoveOutClick(self):
        # click handler for the Move Out button

        self._RequestFocuserMove(self._moveAmount)

    def _OnAbortMoveClick(self):
        # click handler for the Abort Move button

        try:
            self._mgr.HaltFocuser()
        except Exception as e:
            msg = "Unable to abort focuser movement. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)

    def _OnMoveAmountChanged(self, value):
        # handler for value changes to the move amount slider

        mapping = {0: 1, 1: 4, 2: 10, 3: 40, 4: 100, 5: 400, 6: 1000}
        # self._moveAmount = int(mapping.get(self._moveAmountDisplay.get()))
        self._moveAmount = mapping.get(int(value))
        self._moveAmtLabel.config(text=f"{self._moveAmount} steps/move")

    def _OnMoveToBtnClick(self):
        # click handler for the Move To (Go) button

        target = self._moveToAmountDisplay.get()
        delta = target - self._status.Position
        self._RequestFocuserMove(delta)

    def _OnUnitsChanged(self):
        # handler for changes to the temperature units radio buttons

        temp = self._status.Temperature

        if temp != temp:  # if the temperature is NaN it will not be equal to itself.
            # temperature is not available from this focuser
            self._temperatureDisplay.set("NO DATA")
        else:
            if self._temperatureUnitsDisplay.get() == "F":
                # convert to Fahrenheit
                temp = temp * 1.8 + 32.0

            # display with one decimal place
            # self._temperatureDisplay.set(f'{temp:0.1f}')
            tempStr = locale.format_string("%0.1f", temp)
            self._temperatureDisplay.set(tempStr)

    def _OnTempCompStateChanged(self):
        # handler for changes to the state of the temp comp checkbox

        state = True if self._tempCompDisplay.get() == 1 else False
        try:
            self._mgr.SetTemperatureCompensation(state)
        except Exception as e:
            msg = "Unable to set temperature compensation state. "
            msg += "Details follow:\r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)

    def _ParmsListener(self, parms):
        # callback for the parameters update message

        self._parms = parms

    def _StatusListener(self, sts):
        # callback for the status update message

        if self._status is None:
            firstUpdate = True
        else:
            firstUpdate = False

        oldStatus = self._status
        self._status = sts

        # update the connected state

        state = "Connected" if sts.Connected else "Not Connected"
        self._isConnectedDisplay.set(state)

        # update the focuser position, if we have an absolute focuser.

        pos = (str(sts.Position)) if self._parms.Absolute else "NO DATA"
        self._positionDisplay.set(pos)

        # update the focuser temperature, if it is available

        self._OnUnitsChanged()

        # update the temperature compensation checkbox state

        tcValue = 1 if sts.TempComp else 0
        self._tempCompDisplay.set(tcValue)

        # en/disable the move and abort buttons

        if sts.Connected == True:
            moveState = tk.NORMAL
            abortState = tk.DISABLED

            if sts.IsMoving:
                moveState = tk.DISABLED
                abortState = tk.NORMAL
            else:
                self._focuserBusy = False

            self._moveInBtn["state"] = moveState
            self._moveOutBtn["state"] = moveState
            self._abortMoveBtn["state"] = abortState

        # if first update then zero the accumulated total steps and
        # enable the buttons

        if firstUpdate:
            self._accumulatedTotalSteps.set(0)
            self._editTotalStepsBtn["state"] = tk.NORMAL
            self._resetTotalStepsBtn["state"] = tk.NORMAL

        # if this is our first update since connection, set the MoveTo position
        # to the current position

        if firstUpdate:
            self._moveToPositionEntry["state"] = tk.NORMAL
            self._moveToPositionBtn["state"] = tk.NORMAL
            self._moveToAmountDisplay.set(sts.Position)
            self._startingPosition = sts.Position
        else:
            self._startingPosition = oldStatus.Position

        moveState = "Moving" if (sts.IsMoving) else "Stationary"
        self._movementStatusDisplay.set(moveState)

    def _MoveAmountListener(self, amount):
        # callback for move update messages

        total = self._accumulatedTotalSteps.get() + amount
        self._accumulatedTotalSteps.set(total)

    def _DisconnectListener(self):
        # callback for disconnect messages

        # on disconnect, some widgets are reset by the StatusListener. Others
        # are reset here.

        nd = "NO DATA"
        self._positionDisplay.set(nd)
        self._moveInBtn["state"] = tk.DISABLED
        self._moveOutBtn["state"] = tk.DISABLED
        self._abortMoveBtn["state"] = tk.DISABLED
        self._accumulatedTotalSteps.set(0)
        self._stepEntry["state"] = "readonly"
        self._editTotalStepsBtn["state"] = tk.DISABLED
        self._resetTotalStepsBtn["state"] = tk.DISABLED
        self._moveToPositionEntry["state"] = tk.DISABLED
        self._moveToAmountDisplay.set(0)
        self._moveToPositionBtn["state"] = tk.DISABLED
        self._movementStatusDisplay.set(nd)

    def _RequestFocuserMove(self, delta):
        # single point to request focuser movement

        retval = True

        try:
            self._mgr.MoveFocuserBy(delta)
            self._focuserBusy = True
        except Exception as e:
            msg = "An error was occurred when attempting a focuser move. "
            msg += "Details follow: \r\n\r\n"
            self._ShowExceptionError(self._ERROR_TITLE, msg, e)
            retval = False

        return retval

    def _OnEditStepsClick(self):
        # click handler for the Edit Accumulated Total Steps button

        if not self._status.Connected:
            return

        # toggle the Entry widget button between normal and readonly states

        entState = self._stepEntry["state"]
        entState = tk.NORMAL if entState == "readonly" else "readonly"
        self._stepEntry.config(state=entState)

    def _OnResetStepsClick(self):
        # click handler for the Reset Total Steps button
        self._accumulatedTotalSteps.set(0)

    def _ShowExceptionError(self, title, message, xcp):
        msg = message
        formatter = ExceptionFormatter.GetInstance()
        msg += formatter.Format(xcp)
        root = self._parent
        messagebox.showerror(title, msg, parent=root)

    # End of Private Properties and Methods
