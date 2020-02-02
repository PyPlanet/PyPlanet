from pyplanet.core.events import Signal as _Signal
from pyplanet.core.events.manager import SignalManager as _SignalManager

menu_add_entry = _Signal(code='menu_add_entry', namespace='menu')
menu_remove_entry = _Signal(code='menu_remove_entry', namespace='menu')

_SignalManager.register_signal([menu_add_entry, menu_remove_entry])
