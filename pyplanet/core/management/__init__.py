import argparse
import os

import sys

from pyplanet.conf import settings
from pyplanet.god.process import EnvironmentProcess


class Management:

	def __init__(self, argv=None):
		self.argv = argv or sys.argv
		self.parser = argparse.ArgumentParser(prog=self.argv.pop(0))
		self.arguments = object()
		self.add_arguments()

	def add_arguments(self):
		self.parser.add_argument('--settings')
		# TODO.

	def execute(self):
		# Parse arguments.
		self.arguments = self.parser.parse_args(self.argv)

		# Start Controller.
		print(settings.DEBUG)

		# Start god.
		processes = list()
		for env in ['default']:
			processes.append(EnvironmentProcess(environment_name=env))

		# Starting all processes.
		for process in processes:
			process.process.start()


def start(argv=None):
	"""
	Run the utility from CLI.
	:param argv: arguments.
	"""
	utility = Management(argv)
	utility.execute()
