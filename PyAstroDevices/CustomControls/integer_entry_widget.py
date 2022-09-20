from tkinter import Tk, Entry

class IntegerEntry(Entry):
	"""
	Subclass of the tkinter Entry widget with validation to prevent entry of
	characters that would cause the entry text to not be formattable as a
	floating point number. 

	Plus and minus signs are optional but must be the first character.
	Only one decimal point is allowed
	The remaining characters must be digits from 0 thru 9.
	"""
	
	def __init__(self, *args, **kwargs):
		# IntegerEntry initializer configures input validation

		super().__init__(*args, **kwargs)

		vcmd = (self.register(self._validate),'%P')
		self.config(validate="all", validatecommand=vcmd)

	def _validate(self, text):
		# performs validation of the entered characters to ensure that
		# the entered value is convertible to an integer number

		# check that all characters are valid
		# "-" is the first character or not present
		# "+" is the first character or not present
		if (all(char in "0123456789+-" for char in text) and  
			"-" not in text[1:] and 
			"+" not in text[1:]): 
			return True
		else:
			return False    


