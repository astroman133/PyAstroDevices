import locale

from tkinter import Tk, Entry


class FloatEntry(Entry):
    """
    Subclass of the tkinter Entry widget with validation to prevent entry of
    characters that would cause the entry text to not be formattable as a
    floating point number.

    Plus and minus signs are optional but must be the first character.
    Only one decimal point is allowed
    The remaining characters must be digits from 0 thru 9.
    """
    def __init__(self, *args, **kwargs):
        """
        FloatEntry initializer configures input validation
        """
        super().__init__(*args, **kwargs)

        vcmd = (self.register(self._Validate), "%P")
        self.config(validate="all", validatecommand=vcmd)

    def _Validate(self, text):
        # performs validation of the entered characters to ensure that
        # the entered value is convertible to a floating point number
        decsep = locale.localeconv()["decimal_point"]
        vchars = "0123456789+-" + decsep
        # check that all characters are valid
        # "-" is the first character or not present
        # "+" is the first character or not present
        # only 0 or 1 decimal separators
        if (
            all(char in vchars for char in text)
            and "-" not in text[1:]
            and "+" not in text[1:]
            and text.count(decsep) <= 1
        ):

            return True
        else:
            return False
