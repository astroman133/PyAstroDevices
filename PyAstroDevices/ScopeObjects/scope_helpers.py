import math
import locale
from enum import Enum

from enum_switch import Switch
from alpaca.telescope import *


class NudgeDirection(Enum):
    """
    An enumeration of nudge directions to support nudging a telescope via
    MoveAxis calls
    """

    Nothing = -1
    North = 0
    South = 1
    East = 2
    West = 3


class NudgeRate:
    """
    A simple class to contain a rate value (Rate) and a descriptor (Name)
    """

    def __init__(self, name="", rate=float("nan")):
        self._name = name
        self._rate = rate

    @property
    def Name(self):
        return self._name

    @Name.setter
    def Name(self, value):
        self._name = value

    @property
    def Rate(self):
        return self._rate

    @Rate.setter
    def rate(self, value):
        self._rate = value


class SlewDirection:
    """
    Class to contain the name and description for a slew direction.
    For example name = 'N' and description = 'North'
    """

    def __init__(self, name, description):
        self._name = name
        self._description = description

    @property
    def Name(self):
        return self._name

    @property
    def Description(self):
        return self._description


class DriveRatesSwitch(Switch):
    """
        This class uses the enum_switch module to derive from the Switch class
        This gives us the ability to provide friendly names for
    the Alpaca DriveRates enumeration.
    """

    def driveSidereal(self):
        return "Sidereal"

    def driveLunar(self):
        return "Lunar"

    def driveSolar(self):
        return "Solar"

    def driveKing(self):
        return "King"


class PierSideSwitch(Switch):
    """
    This class uses the enum_switch module to derive from the Switch class
    This gives us the ability to provide friendly names for
    the Alpaca PierSide enumeration.
    """

    def pierEast(self):
        return "East"

    def pierWest(self):
        return "West"

    def pierUnknown(self):
        return "Unknown"


class NudgeRates:
    """
    This class encapsulates the logic to create and return valid axis rates
    based on the values by a call to the telescope's AxisRates method.

    All the methods are static (class) methods and to not need an instance of
    the class to be created.
    """

    _SIDEREAL_RATE = 0.0042  # degrees per second

    @classmethod
    def DefaultNudgeRates(cls):
        rates = []

        rates.append(NudgeRate("16X Sidereal", 0.06648))
        rates.append(NudgeRate("64X Sidereal", 0.26594))
        rates.append(NudgeRate("2 deg/sec", 2.0))

        return rates

    @classmethod
    def FromAxisRates(cls, axisRates):
        """
        Takes a list of axisRate objects and returns a list of valid rates
        to use for nudging the telescope

        Positional arguments:
        axisRates -- a collection of IAxisRate objects from a telescope driver

        Returns -- a collection of valid NudgeRate objects
        """
        rates = None

        if axisRates is not None and len(axisRates) > 0:
            rates = []

            if cls._AreDiscreteRates(axisRates):
                rates = cls._CreateDiscreteNudgeRates(axisRates)
            else:
                rates = cls._CreateRangedNudgeRates(axisRates)

        return rates

    @classmethod
    def _AreDiscreteRates(cls, axisRates):
        # helper method to determine of the min value is equal to the max
        # value for every rate

        retval = True

        if axisRates is None or len(axisRates) == 0:
            retval = False
        else:
            for rate in axisRates:
                if (rate.Maximum - rate.Minimum) > 0.001:
                    retval = False
                    break

        return retval

    @classmethod
    def _CreateDiscreteNudgeRates(cls, axisRates):
        # create a list of valid nudge rates for a discrete list
        # of axis rates.
        nudgeRates = []

        for rate in axisRates:
            # this is a discrete rate value

            nudgeRate = cls._BuildNudgeRate(rate.Minimum)

            nudgeRates.append(nudgeRate)

        if len(nudgeRates) == 0:
            nudgeRates = None

        return nudgeRates

    @classmethod
    def _CreateRangedNudgeRates(cls, axisRates):
        # create a list of valid nudge rates for a given list of
        # discontinuous axis rates
        nudgeRates = None

        if axisRates is None or len(axisRates) == 0:
            return nudgeRates

        if len(axisRates) == 1:
            nudgeRates = cls.DefaultNudgeRates()

            if (
                nudgeRates[0].Rate > axisRates[0].Minimum
                and nudgeRates[len(nudgeRates) - 1].Rate < axisRates[0].Maximum
            ):

                # here the default rates are valid, so use them.

                return nudgeRates

        # we can't use the default nudge rates, so build a valid list.
        # the provided list of valid axis rates consists of multiple ranges, so just take the
        # midpoint of each range

        nudgeRates = []

        for axisRate in axisRates:
            rateValue = (axisRate.Minimum + axisRate.Maximum) / 2.0
            nudgeRate = cls._BuildNudgeRate(rateValue)
            nudgeRates.append(nudgeRate)

        return nudgeRates

    @classmethod
    def _BuildNudgeRate(cls, rateValue):
        # builds a NudgeRate object for a given rate value

        rateStr = cls._GetRateString(rateValue)

        return NudgeRate(rateStr, rateValue)

    @classmethod
    def _GetRateString(cls, rateValue):
        # creates a rate string for the passed rate value
        # Values less than .5 degrees/sec are described as some multiple of
        # the sidereal rate.
        retval = None

        if rateValue < 0.5:
            factor = cls._GetSiderealRateFactor(rateValue)
            retval = f"{factor}X Sidereal"
        else:
            # retval = f'{rateValue:.2f} deg/sec'
            retval = locale.format_string("%.2f", rateValue) + " deg/sec"

        return retval

    @classmethod
    def _GetSiderealRateFactor(cls, rateValue):
        # calculate the sidereal rate factor from a rate value.
        return int(round(rateValue / cls._SIDEREAL_RATE, 0))


class Formatter:
    """
    This class different types of numeric data, like times and degrees and
    formats them as hours, minutes, and seconds or degrees, minutes, and
    seconds that are suitable for display.
    """

    @staticmethod
    def GetTimeString(timeValue: float):
        """
        Convert a floating point value representing hours such as a right
        ascension or hour angle to a display string

        Positional arguments:
        timeValue -- an hour value to be converted

        Returns -- the formatted string
        """
        sign = 1.0

        if math.isnan(timeValue):
            return "NO DATA"

        if timeValue < 0:
            sign = -1.0

        seconds = timeValue * 3600 * sign
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60

        # Since we are displaying seconds without a decimal place, that a 
        # value of 59.99 seconds could be rounded up to 60 seconds. If we see
        # this situation we need to set it to 0 and increment the minutes.

        if round(seconds, 0) == 60:
            seconds = 0
            minutes += 1

        # If the minutes rounds to 60 then we need to reset it to 0 and increment the hour.

        if round(minutes, 0) == 60:
            minutes = 0
            hour += 1

        # if we have rounded up the hour to 24, then re-set it to 0.

        if hour == 24:
            hour = 0

        return f'{hour*sign:.0f}h {minutes:.0f}m {seconds:.0f}s'

    @staticmethod
    def GetDegreesString(degreesValue: float):
        """
        Convert a floating point value representing degrees, such as a
        declination or azimuth, to a display string

        Positional arguments:
        degreesValue -- an degree value to be converted

        Returns -- the formatted string
        """
        sign = 1.0

        if math.isnan(degreesValue):
            return "NO DATA"

        if degreesValue < 0:
            sign = -1.0

        seconds = degreesValue * 3600.0 * sign
        degrees = seconds // 3600.0
        seconds %= 3600
        minutes = seconds // 60.0
        seconds %= 60.0

        # Since we are displaying seconds without a decimal place, a value
        # of 59.99 seconds could be rounded up to 60 seconds. If we see
        # this situation we need to set it to 0 and increment the minutes.

        if round(seconds, 0) == 60:
            seconds = 0.0
            minutes += 1

        # If the minutes rounds to 60 then we need to reset it to 0 and increment
        # the degrees.

        if round(minutes, 0) == 60:
            minutes = 0
            degrees += 1

        # At this point the value should not be greater the max allowable, 
        # even though we have rounded up.

        return f'{degrees*sign:.0f}{chr(176)} {minutes:.0f}\' {seconds:.0f}"'

class Validator:
    @staticmethod
    def InRange(fValue, fMinValue, bMinEqual, fMaxValue, bMaxEqual):
        """
        Tests whether a value is within a given range

        Positional arguments:
        fValue -- the value to be tested
        fMinValue -- the minimum value of the test range
        bMinEqual -- if True, the test value can be equal to the min value
        fMaxValue -- the maximum value of the test range
        bMaxEqual -- if True, the test value can be equal to the max value

        Returns: True if the value is in the provided range, otherwise False
        """
        if bMinEqual and fValue < fMinValue:
            return False

        if not bMinEqual and fValue <= fMinValue:
            return False

        if bMaxEqual and fValue > fMaxValue:
            return False

        if not bMaxEqual and fValue >= fMaxValue:
            return False

        return True
