"""
The UI Properties will be set and hold in the class definition bellow.
"""
import json
import logging
import xmltodict as xd

from pyplanet.core.signals import pyplanet_start_after
from pyplanet.core.ui.exceptions import UIPropertyDoesNotExist
from pyplanet.utils.functional import empty

logger = logging.getLogger(__name__)


class UIProperties:  # pragma: no cover
	"""
	Set the custom Script UI Properties.

	.. tip::

		Look at the possible UI Properties right here:

		- Trackmania: https://github.com/maniaplanet/script-xmlrpc/blob/master/XmlRpcListing.md#trackmaniauisetproperties
		- Shootmania: https://github.com/maniaplanet/script-xmlrpc/blob/master/XmlRpcListing.md#shootmaniauisetproperties
		- TM2020: Undocumented by Nadeo, check in-game tool OpenPlanet and discover what properties exist and what it means.

	Access this class with:

	.. code-block:: python

		self.instance.ui_manager.properties
	"""
	specials = ('_properties', '_instance')

	def __init__(self, instance):
		"""
		:param instance: Instance
		:type instance: pyplanet.core.instance.Instance
		"""
		self._instance = instance
		self._raw = None
		self._properties = dict()
		self._update_properties = dict()

	@property
	def properties(self):
		if self._instance.game.game in ['tm', 'sm']:
			if 'ui_properties' in self._properties:
				return self._properties['ui_properties']
		else:
			if self._properties:
				return self._properties
		return False

	async def on_start(self):
		await self.reset()
		await self.refresh_properties()
		self._instance.signals.listen(pyplanet_start_after, self.send_properties)

	async def reset(self):
		"""
		Reset the UI Properties to the default ManiaPlanet ones.
		:return:
		"""
		if self._instance.game.game == 'tm':
			method = 'Trackmania.UI.ResetProperties'
		elif self._instance.game.game == 'sm':
			method = 'Shootmania.UI.ResetProperties'
		else:
			method = 'Common.UIModules.ResetProperties'
		try:
			logger.debug('Resetting UIProperties...')
			await self._instance.gbx.script(method, response_id=False)
		except Exception as e:
			logger.warning('Unable to reset UIProperties: {}'.format(str(e)))

	async def refresh_properties(self):
		if self._instance.game.game == 'tm':
			method = 'Trackmania.UI.GetProperties'
		elif self._instance.game.game == 'sm':
			method = 'Shootmania.UI.GetProperties'
		else:
			method = 'Common.UIModules.GetProperties'
		try:
			if self._instance.game.game == 'tm' or self._instance.game.game == 'sm':
				self._raw = await self._instance.gbx(method, timeout=2)
				self._properties = xd.parse(self._raw['raw_1'])
			else:
				self._raw = await self._instance.gbx(method, timeout=2)
				self._properties = dict()
				for entry in self._raw['uimodules']:
					self._properties[entry['id']] = entry
		except Exception as e:
			self._properties = dict()
			self._raw = None

	def set_visibility(self, element: str, visible: bool):
		"""
		Set the visibility of the UI Property and don't complain about failing to set. Must be set at the start of the
		app(s).

		:param element: Element name, such as notices, map_info and chat.
						Full list: https://github.com/maniaplanet/script-xmlrpc/blob/master/XmlRpcListing.md#shootmaniauisetproperties
		:param visible: Boolean if the element should be visible.
		:return: Boolean, true if is set, false if failed to set.
		"""
		return self.set_attribute(element, 'visible', 'true' if visible else 'false')

	def get_visibility(self, element: str, default=empty):
		"""
		Set the visibility of the UI Property and don't complain about failing to set. Must be set at the start of the
		app(s).

		:param element: Element name, such as notices, map_info and chat.
						Full list: https://github.com/maniaplanet/script-xmlrpc/blob/master/XmlRpcListing.md#shootmaniauisetproperties
		:param default: The default value, or an exception if not given.
		:return: The boolean if it's visible or raise exception if not exists (or the default if default is given).
		"""
		value = self.get_attribute(element, 'visible', default)
		if isinstance(value, str):
			if value.lower() == 'true':
				return True
			elif value.lower() == 'false':
				return False
		return value

	def set_attribute(self, element: str, attribute: str, value):
		"""
		Set an attribute of an element and silent if it's not found. Useful to change positions but unsure if it will
		and still exists. Returns boolean if it's set successfully.

		:param element: Element name
		:param attribute: Attribute name
		:param value: New value of the attribute.
		:return: Boolean if it's set correctly.
		"""
		if not self._properties:
			return False
		if self._instance.game.game in ['tm', 'sm']:
			if element not in self.properties:
				return False
			if '@{}'.format(attribute) not in self.properties[element]:
				return False
			self.properties[element]['@{}'.format(attribute)] = value
		else:
			if element not in self.properties:
				return False

			self.properties[element][attribute] = value
			if element not in self._update_properties:
				self._update_properties[element] = dict(id=element)
			self._update_properties[element][attribute] = value
			self._update_properties[element]['{}_update'.format(attribute)] = True
		return True

	def get_attribute(self, element: str, attribute: str, default=empty):
		"""
		Get an attribute value of an element.

		:param element: Element name
		:param attribute: Attribute name
		:param default: Default if not found.
		:return: Boolean if it's set correctly.
		"""
		if not self._properties:
			if default is not empty:
				return default
			raise UIPropertyDoesNotExist('UI Properties are not present')
		if element not in self.properties:
			if default is not empty:
				return default
			raise UIPropertyDoesNotExist('UI Properties has no element with name \'{}\''.format(element))
		if self._instance.game.game in ['tm', 'sm'] and '@{}'.format(attribute) not in self.properties[element]:
			if default is not empty:
				return default
			raise UIPropertyDoesNotExist('UI Properties has no attribute with name \'{}\''.format(attribute))
		elif attribute not in self.properties[element]:
			if default is not empty:
				return default
			raise UIPropertyDoesNotExist('UI Properties has no attribute with name \'{}\''.format(attribute))

		if self._instance.game.game in ['tm', 'sm']:
			return self.properties[element]['@{}'.format(attribute)]
		return self.properties[element][attribute]

	async def send_properties(self, **kwargs):
		if not self._properties or (self._instance.game.game in ['tm', 'sm'] and 'ui_properties' not in self._properties):
			return

		# Decide the method to use.
		if self._instance.game.game == 'tm':
			method = 'Trackmania.UI.SetProperties'
		elif self._instance.game.game == 'sm':
			method = 'Shootmania.UI.SetProperties'
		else:
			method = 'Common.UIModules.SetProperties'

		if self._instance.game.game in ['tm', 'sm']:
			# Create XML document
			try:
				xml = xd.unparse(self._properties, full_document=False, short_empty_elements=True)
			except Exception as e:
				logger.warning('Can\'t convert UI Properties to XML document! Error: {}'.format(str(e)))
				return

			try:
				await self._instance.gbx(method, xml, encode_json=False, response_id=False)
			except Exception as e:
				logger.warning('Can\'t send UI Properties! Error: {}'.format(str(e)))
				return
		else:
			# Update TM2020 properties.
			try:
				await self._instance.gbx(
					method,
					json.dumps(dict(uimodules=list(self._update_properties.values()))),
					encode_json=False, response_id=False
				)
				logger.debug('UI Properties send and reloaded')
			except Exception as e:
				logger.warning('Can\'t send UI Properties! Error: {}'.format(str(e)))
				return
