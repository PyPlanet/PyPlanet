"""
The setting contrib contains code for managing and providing settings contexts.
"""

from .setting import Setting
from .manager import GlobalSettingManager

__all__ = [
	'Setting',
	'GlobalSettingManager',
]
