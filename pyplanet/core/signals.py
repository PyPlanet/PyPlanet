"""
This file contains the core signals, related to the controller itself.
"""
from pyplanet.core.events import Signal as _Signal
from pyplanet.core.events.manager import SignalManager

pyplanet_start = _Signal(code='start', namespace='pyplanet')
"""
Fired when PyPlanet has finished starting up all core and apps logic.
"""

__all__ = [
	'pyplanet_start'
]

SignalManager.register(pyplanet_start)
