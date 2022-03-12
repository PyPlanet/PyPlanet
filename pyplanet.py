#!/usr/bin/env python3
"""
Bootstrap script of the PyPlanet Controller.
"""
from dotenv import load_dotenv

if __name__ == '__main__':
	load_dotenv()

	from pyplanet.core.management import execute_from_command_line
	execute_from_command_line()
