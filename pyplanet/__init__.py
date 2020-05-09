"""
PyPlanet, a robust and simple Maniaplanet Server Controller for Python 3.6+.
Please see LICENSE file in root of project.
"""
try:
	import subprocess
	__version__ = '{}'.format(subprocess.check_output(["git", "describe", "--always"]).strip().decode())
except Exception as e:
	__version__ = '0.8.0-rc1'
	pass

# __version__ = '1.0.0-dev'
__author__ = 'Tom Valk'
