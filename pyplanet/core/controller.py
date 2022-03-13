"""
This file contains the static entry point to access the controller instance from anywhere without having a reference
to it and to prevent issues with circular imports.

Please import this from the ``pyplanet.core`` package instead!
"""


class _Controller:
	def __init__(self, *args, **kwargs):
		self.__instance = None

	def prepare(self):
		from pyplanet.core.instance import Instance

		self.__instance = Instance()
		return self

	@property
	def instance(self):
		"""
		Get active instance in current process.

		:return: Controller Instance
		:rtype: pyplanet.core.instance.Instance
		"""
		return self.__instance

Controller = _Controller()
"""
Controller access point to prevent circular imports. This is a lazy provided way to get the instance from anywhere!
"""
