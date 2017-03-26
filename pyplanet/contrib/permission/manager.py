from pyplanet.core.events import receiver
from pyplanet.core import signals


class PermissionManager:
	def __init__(self, instance):
		"""
		Initiate, should only be done from the core instance.
		:param instance: Instance.
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		# Initiate the self instances on receivers.
		self.handle_startup()

	@receiver(signals.pyplanet_start_apps_before)
	async def handle_startup(self, **kwargs):
		"""
		Handle startup, just before the apps will start. We will make sure we are ready to get requests for permissions
		:param kwargs: Ignored parameters.
		"""
		pass
