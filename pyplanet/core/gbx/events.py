"""
This file describes the XML event signals.
"""
import logging

from pyplanet.core.events import Signal, Callback


def register():
	logging.debug('Registering core and well-known callbacks...')
