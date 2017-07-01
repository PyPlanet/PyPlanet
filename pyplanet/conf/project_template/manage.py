#!/usr/bin/env python3
import os
import sys

if __name__ == '__main__':

	# Use Python for the configuration
	os.environ.setdefault('PYPLANET_SETTINGS_METHOD', 'python')
	os.environ.setdefault('PYPLANET_SETTINGS_MODULE', 'settings')

	# Use YAML for configuration (comment other options and uncomment the following two lines).
	# os.environ.setdefault('PYPLANET_SETTINGS_METHOD', 'yaml')
	# os.environ.setdefault('PYPLANET_SETTINGS_DIRECTORY', 'settings')
	# Will search for two files in the directory: base.yaml and apps.yaml. See http://pypla.net for more information.

	# Use JSON for configuration (comment other options and uncomment the following two lines).
	# os.environ.setdefault('PYPLANET_SETTINGS_METHOD', 'json')
	# os.environ.setdefault('PYPLANET_SETTINGS_DIRECTORY', 'settings')
	# Will search for two files in the directory: base.json and apps.json. See http://pypla.net for more information.

	try:
		from pyplanet.core.management import execute_from_command_line
	except ImportError as exc:
		raise ImportError(
			'Couldn\'t import PyPlanet. Are you sure it\'s installed and '
			'available on your PYTHONPATH environment variable? Did you '
			'forget to activate a virtual environment?'
		) from exc
	execute_from_command_line(sys.argv)
