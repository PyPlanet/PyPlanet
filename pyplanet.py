#!/usr/bin/env python3
"""
Bootstrap script of the PyPlanet Controller.
"""
import os

if __name__ == '__main__':
	# Set the settings options.
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

	from pyplanet.core.management import execute_from_command_line
	execute_from_command_line()
