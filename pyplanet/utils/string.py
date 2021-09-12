from string import Formatter

class ExtendedFormatter(Formatter):
	def convert_field(self, value, conversion):
		if conversion == 'l':
			return str(value).lower()
		elif conversion == 'u':
			return str(value).upper()
		elif conversion == 'c':
			return str(value).capitalize()
		return super().convert_field(value, conversion)

