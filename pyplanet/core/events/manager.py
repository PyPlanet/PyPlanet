"""
The events manager contains the class that manages custom and abstract callbacks into the system callbacks.
Once a signals is registered here it could be used by string reference. This makes it easy to have dynamically signals
being created by other apps in a single place so it could be used over all apps.

For example you would create your own custom signal if you have a app for your own created game mode script that abstracts
all the raw XML-RPC events into nice structured and maybe even including fetched data from external sources.
"""
import importlib
import os


class SignalManager:
	def __init__(self):
		self.signals = dict()

		self.namespaces = list()

		# This var is used to temporary override namespaces when processing apps.
		self._current_namespace = None

	def register(self, signal, app=None):
		if not getattr(signal, 'Meta', None):
			raise Exception('Signal class should have the Meta class inside.')
		if not getattr(signal.Meta, 'code', None):
			raise Exception('Signal Meta class has no code defined!')
		if not getattr(signal.Meta, 'namespace', None) and self._current_namespace:
			namespace = self._current_namespace
		elif getattr(signal.Meta, 'namespace', None):
			namespace = signal.Meta.namespace
		else:
			namespace = None # TODO: How to handle this, will we go for the exception?
		code = signal.Meta.code

		instance = signal()
		signal_code = '{}:{}'.format(namespace, code)

		print('Registering ', signal_code)

	def init_app(self, app):
		"""
		Initiate app, load all signal files. (just import, they should register with decorators).
		:param app: App instance
		:type app: pyplanet.apps.AppConfig
		"""
		self._current_namespace = app.label

		root_path = app.path

		# Import the signals module.
		try:
			importlib.import_module('{}.signals'.format(app.name))
		except ImportError:
			pass
		self._current_namespace = None

Manager = SignalManager()


def public_signal(cls):


	Manager.register(cls)
	return cls
