#!/usr/bin/env python
"""
Bootstrap script of the PyPlanet Controller.
"""
import os

if __name__ == '__main__':
	# Set the local settings module.
	os.environ.setdefault('PYPLANET_SETTINGS_MODULE', 'app.settings')

	from pyplanet.core.management import start
	start()
