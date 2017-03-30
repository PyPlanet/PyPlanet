from pyplanet.utils import times


def test_time_parsing():
	raw = 14004
	expect = '0:14.004'
	assert times.format_time(raw) == expect

	raw = 20135
	expect = '0:20.135'
	assert times.format_time(raw) == expect

	raw = 65195
	expect = '1:05.195'
	assert times.format_time(raw) == expect

	raw = 605195
	expect = '10:05.195'
	assert times.format_time(raw) == expect

	raw = 6005195
	expect = '01:40:05.195'
	assert times.format_time(raw) == expect
