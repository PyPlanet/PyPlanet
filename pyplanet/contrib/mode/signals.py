"""
This file contains the contrib mode signals, related to the current script/mode.
"""
from pyplanet.core.events import Signal as _Signal, handle_generic
from pyplanet.core.events.manager import SignalManager as _SignalManager


script_mode_changed = _Signal(
	code='script_mode_changed',
	namespace='contrib.mode',
	process_target=handle_generic
)
"""
Is called after a new script has been loaded and became active!. Reporting two parameters:

:param unloaded_script: Old script name.
:param loaded_script: New and just loaded script.
"""

_SignalManager.register_signal([
	script_mode_changed
])
