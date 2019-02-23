import math


def format_time(time, hide_hours_when_zero=True, hide_milliseconds=False):
	"""
	Format time from integer milliseconds to string format that could be displayed to the end-user.
	
	:param time: Integer time in milliseconds.
	:type time: int
	:param hide_hours_when_zero: Hide the hours when there are zero hours.
	:type hide_hours_when_zero: bool
	:param hide_milliseconds: Hide the milliseconds.
	:type hide_milliseconds: bool
	:return: String output
	:rtype: str
	"""
	hours = math.floor((time / 1000 / 60 / 60))
	minutes = math.floor((time - (hours * 60 * 60 * 1000)) / 1000 / 60)
	seconds = math.floor((time - (hours * 60 * 60 * 1000) - (minutes * 60 * 1000)) / 1000)
	millis = (time - (hours * 60 * 60 * 1000) - (minutes * 60 * 1000) - (seconds * 1000))

	formatted_time = ''
	if hours > 0 or not hide_hours_when_zero:
		formatted_time += '{:02d}:{:02d}:'.format(hours, minutes)
	else:
		formatted_time += '{}:'.format(str(minutes))
	if hide_milliseconds:
		return formatted_time + '{:02d}'.format(seconds)
	return formatted_time + '{:02d}.{:03d}'.format(seconds, millis)
