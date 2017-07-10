"""
This folder contains the configuration in different files. This init file imports all files in the current directory
to make sure we combine configurations to one settings module.
Documentation: http://pypla.net/

If you want to use other configuration methods like YAML or JSON files, take a look at http://pypla.net/ and head to the
configuration pages.
"""

from .base import *
from .apps import *

try:
	from .local import *
except:
	pass
