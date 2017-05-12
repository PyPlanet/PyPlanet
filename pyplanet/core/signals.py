"""
This file contains the core signals, related to the controller itself.
"""
from pyplanet.core.events import Signal as _Signal
from pyplanet.core.events.manager import SignalManager as _SignalManager

pyplanet_start_before		= _Signal(code='start_before', namespace='pyplanet')
pyplanet_start_after		= _Signal(code='start_after', namespace='pyplanet')

pyplanet_start_gbx_before	= _Signal(code='start_gbx_before', namespace='pyplanet')
pyplanet_start_gbx_after	= _Signal(code='start_gbx_after', namespace='pyplanet')

pyplanet_start_db_before	= _Signal(code='start_db_before', namespace='pyplanet')
pyplanet_start_db_after		= _Signal(code='start_db_after', namespace='pyplanet')

pyplanet_start_apps_before	= _Signal(code='start_apps_before', namespace='pyplanet')
pyplanet_start_apps_after	= _Signal(code='start_apps_after', namespace='pyplanet')

pyplanet_performance_mode_begin = _Signal(code='start_performance_mode', namespace='pyplanet')
pyplanet_performance_mode_end	= _Signal(code='end_performance_mode', namespace='pyplanet')

_SignalManager.register_signal([
	pyplanet_start_before, pyplanet_start_after, pyplanet_start_gbx_before ,pyplanet_start_gbx_after,
	pyplanet_start_db_before, pyplanet_start_db_after, pyplanet_start_apps_before, pyplanet_start_apps_after,
	pyplanet_performance_mode_begin, pyplanet_performance_mode_end
])
