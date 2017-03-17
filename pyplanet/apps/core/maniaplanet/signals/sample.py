from pyplanet.core import events


@events.public_signal
class SampleSignal(events.Signal):
	class Meta:
		code = 'sample'
