class MapManager:
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		self._matchsettings = None
		self._maps = list()
		self._current = None

