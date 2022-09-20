from traceback import format_exception


class ExceptionFormatter(object):
    """
    A singleton class to format exceptions using the Python builtin
    exception formatter method.
    """
    _instance = None

    @staticmethod
    def GetInstance():
        """
        Provides access to the singleton instance, creating the instance if it
        does not already exist

        Returns -- the instance of ExceptionFormatter
        """
        # Static Access Method

        if ExceptionFormatter._instance is None:
            ExceptionFormatter()

        return ExceptionFormatter._instance

    def __init__(self):
        # the class instance initializer

        if ExceptionFormatter._instance is not None:
            raise Exception("The ExceptionFormatter class is a singleton!")

        ExceptionFormatter._instance = self

    def Format(self, exc):
        """
        Format the exception

        Positional arguments:
        exc -- the exception to be formatted

        Returns -- a string with the formatted exception information
        """
        list = format_exception(exc, limit=1, chain=False)

        return "".join(list)
