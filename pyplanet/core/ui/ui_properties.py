"""
The UI Properties will be set and hold in the class definition bellow.
"""
from xml.etree import cElementTree as et

from pyplanet.core.signals import pyplanet_start_after


class UIProperties:  # pragma: no cover
	"""
	Access this class with:

	.. code-block:: python

		self.instance.ui_manager.properties
	"""

	def __init__(self, instance):
		"""
		:param instance: Instance
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance

		self._properties = dict()

	@property
	def properties(self):
		return self._properties

	async def on_start(self):
		await self.refresh_properties()
		self._instance.signal_manager.listen(pyplanet_start_after, self.on_ready)

	async def refresh_properties(self):
		if self._instance.game.game == 'tm':
			method = 'Trackmania.UI.GetProperties'
		else:
			method = 'Shootmania.UI.GetProperties'
		try:
			self._properties = await self._instance.gbx(method)
		except:
			self._properties = dict()

	async def on_ready(self, **kwargs):
		if not self._properties:
			return

		xml = self.get_xml()
		print(xml)

		# TODO: Send props.
		pass

	def get_xml(self):
		root = et.Element('ui_properties')
		et.SubElement(root, 'map_info', visible=self._properties.get('map_info'))
		pass


		return et.tostring(root, encoding='utf-8')
