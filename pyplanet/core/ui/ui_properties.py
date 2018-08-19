"""
The UI Properties will be set and hold in the class definition bellow.
"""
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
		self._raw_start = """
		<ui_properties>
				<!-- The map name and author displayed in the top right of the screen when viewing the scores table -->
				<map_info visible="false" pos="-160. 80. 150." />
				<!-- Information about live envent displayed in the top right of the screen -->
				<live_info visible="false" pos="-159. 84. 5." />
				<!-- Information about the spectated player displayed in the bottom of the screen -->
				<spectator_info visible="true" pos="0. -68. 5." />
				<!-- Only visible in solo modes, it hides the medal/ghost selection UI -->
				<opponents_info visible="true" />
				<!--
					The server chat displayed on the bottom left of the screen
					The offset values range from 0. to -3.2 for x and from 0. to 1.8 for y
					The linecount property must be between 0 and 40
				-->
				<chat visible="true" offset="0. 0." linecount="7" />
				<!-- Time of the players at the current checkpoint displayed at the bottom of the screen -->
				<checkpoint_list visible="false" pos="48. -52. 5." />
				<!-- Small scores table displayed at the end of race of the round based modes (Rounds, Cup, ...) on the right of the screen -->
				<round_scores visible="false" pos="-158.5 40. 150." />
				<!-- Race time left displayed at the bottom right of the screen -->
				<countdown visible="true" pos="134. -73. 10." />
				<!-- 3, 2, 1, Go! message displayed on the middle of the screen when spawning -->
				<go visible="true" />
				<!-- Current race chrono displayed at the bottom center of the screen -->
				<chrono visible="true" pos="0. -84. -5." />
				<!-- Speed and distance raced displayed in the bottom right of the screen -->
				<speed_and_distance visible="true" pos="137. -69. 5." />
				<!-- Previous and best times displayed at the bottom right of the screen -->
				<personal_best_and_rank visible="false" pos="157. -24. 5." />
				<!-- Current position in the map ranking displayed at the bottom right of the screen -->
				<position visible="true" pos= "0. -70. -5." />
				<!-- Checkpoint time information displayed in the middle of the screen when crossing a checkpoint -->
				<checkpoint_time visible="true" pos="0. 3. -10." />
				<!-- The avatar of the last player speaking in the chat displayed above the chat -->
				<chat_avatar visible="false" />
				<!-- Warm-up progression displayed on the right of the screen during warm-up -->
				<warmup visible="true" pos="153. 13. 0." />
				<!-- Ladder progression box displayed on the top of the screen at the end of the map -->
				<endmap_ladder_recap visible="false" />
				<!-- Laps count displayed on the right of the screen on multilaps map -->
				<multilap_info visible="true" pos="140. 84. 5." />
				<!-- Player's ranking at the latest checkpoint -->
				<checkpoint_ranking visible="false" pos="0. 84. 5." />
				<!-- Scores table displayed in the middle of the screen -->
				<scorestable alt_visible="false" visible="true" />
				<!-- Number of players spectating us displayed at the bottom right of the screen -->
				<viewers_count visible="true" pos="157. -40. 5." />
		</ui_properties>
		"""
		self._properties = dict()

	@property
	def properties(self):
		if 'ui_properties' in self._properties:
			return self._properties['ui_properties']
		return False

	async def on_start(self):
		self._instance.signals.listen(pyplanet_start_after, self.send_start_properties)

	async def refresh_properties(self):
		if self._instance.game.game == 'tm':
			method = 'Trackmania.UI.GetProperties'
		else:
			method = 'Shootmania.UI.GetProperties'
		try:
			self._raw = await self._instance.gbx(method)
			self._properties = xd.parse(self._raw['raw_1'])
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
		if element not in self.properties:
			return False
		if '@{}'.format(attribute) not in self.properties[element]:
			return False
		self.properties[element]['@{}'.format(attribute)] = value
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
		if '@{}'.format(attribute) not in self.properties[element]:
			if default is not empty:
				return default
			raise UIPropertyDoesNotExist('UI Properties has no attribute with name \'{}\''.format(attribute))
		return self.properties[element]['@{}'.format(attribute)]

	async def send_properties(self, **kwargs):
		if not self._properties or 'ui_properties' not in self._properties:
			return

		# Decide the method to use.
		if self._instance.game.game == 'tm':
			method = 'Trackmania.UI.SetProperties'
		else:
			method = 'Shootmania.UI.SetProperties'

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

	async def send_start_properties(self, **kwargs):
		# Decide the method to use.
		self._properties = xd.parse(self._raw_start)

		if self._instance.game.game == 'tm':
			method = 'Trackmania.UI.SetProperties'
		else:
			method = 'Shootmania.UI.SetProperties'
		try:
			await self._instance.gbx(method, self._raw_start, encode_json=False, response_id=False)
		except Exception as e:
			logger.warning('Can\'t send UI Properties! Error: {}'.format(str(e)))
			return
