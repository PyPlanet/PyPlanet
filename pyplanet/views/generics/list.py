import math
import re
import logging
import pandas as pd
import numpy as np

from asyncio import iscoroutinefunction
from peewee import Field

from pyplanet.utils import style

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.db import Model
from pyplanet.views.template import TemplateView

logger = logging.getLogger(__name__)


class ListView(TemplateView):
	"""
	The ListView is an abstract list that uses a database query to show and manipulate the list that is presented to the
	end-user. The ListView is able to automatically manage the searching, ordering and pagination of your query contents.

	The columns could be specified, for each column you can change behaviour, such as searchable and sortable. But also
	custom rendering of the values that will be displayed.

	You can override ``get_fields()``, ``get_actions()``, ``get_query()`` if you need any customization or use a self method
	or variable in one of your properties.

	.. note::

		The design and some behaviour can change in updates of PyPlanet. We aim to provide backward compatibility as much
		as we can. If we are going to break things we will make it deprecated, or if we are in a situation of not having
		enough time to provide a transition time, we are going to create a separate solution (like a second version).

	.. code-block:: python

		class SampleListView(ListView):
			query = Model.select()
			model = Model
			title = 'Select your item'
			fields = [
				{'name': 'Name', 'index': 'name', 'searching': True, 'sorting': True},
				{'name': 'Author', 'index': 'author', 'searching': True, 'sorting': True},
			]
			actions = [
				{
					'name': 'Delete',
					'action': self.action_delete,
					'style': 'Icons64x64_1',
					'substyle': 'Close'
				},
			]

			async def action_delete(self, player, values, instance, **kwargs):
				print('Delete value: {}'.format(instance))

	"""
	query = None
	model = None

	title = None
	icon_style = None
	icon_substyle = None
	fields = []
	actions = []

	template_name = 'core.views/generics/list.xml'

	single_list = True
	"""Change this to False to have multiple lists open at the same time."""

	def __init__(self, *args, **kwargs):
		self.id = 'pyplanet.views.generics.list.ListView'
		super().__init__(*args, **kwargs)
		self.disable_alt_menu = True
		self.search_text = None
		self.sort_field = None
		self.sort_order = 1
		self.page = 1
		self.count = 0
		self.objects = list()

		self.num_per_page = 20

		self.provide_search = True

		#if self.single_list:
			#self.id = 'pyplanet__generics_list'

		# Setup the receivers.
		self.subscribe('list_button_close', self.close)
		self.subscribe('list_button_refresh', self.refresh)
		self.subscribe('list_button_search', self._search)

		self.subscribe('list_button_first', self._first_page)
		self.subscribe('list_button_prev_10', self._prev_10_pages)
		self.subscribe('list_button_prev', self._prev_page)
		self.subscribe('list_button_next', self._next_page)
		self.subscribe('list_button_next_10', self._next_10_pages)
		self.subscribe('list_button_last', self._last_page)

	@property
	def order(self):
		if self.sort_field and isinstance(self.sort_field, Field):
			if self.sort_order and self.sort_field:
				return self.sort_field
			elif not self.sort_order and self.sort_field:
				return -self.sort_field
		elif self.sort_field:
			return self.sort_field
		return None

	async def handle_catch_all(self, player, action, values, **kwargs):
		# Sorting the column:
		if action.startswith('list_header_'):
			match = re.search('^list_header_([0-9]+)$', action)
			if len(match.groups()) != 1:
				return

			try:
				col = int(match.group(1))
				fields = await self.get_fields()
				field = fields[col]
			except Exception as e:
				logger.error('Got invalid result in list column click: {}'.format(e))
				return

			# Check if sorting is defined + true.
			if 'sorting' not in field or not field['sorting'] or not field['index']:
				return

			# Sort on column
			if isinstance(self.model, Model):
				sort_field = getattr(self.model, field['index'])
				current_field_name = self.sort_field.db_column if self.sort_field else None
				field_name = sort_field.db_column
			else:
				sort_field = field
				current_field_name = self.sort_field['index'] if self.sort_field else None
				field_name = sort_field['index']

			if self.sort_field and current_field_name == field_name:
				if self.sort_order == 1:
					self.sort_order = 0
				else:
					# Unsort. clear sorting
					self.sort_field = None
					self.sort_order = 0
			else:
				self.sort_field = sort_field
				self.sort_order = 1

			# Refresh list
			await self.refresh(player)

		elif action.startswith('list_body_') or action.startswith('list_action_'):
			if action.startswith('list_body_'):
				match = re.search('^list_body_([0-9]+)_([0-9]+)$', action)
				trigger = 'body'
			else:
				match = re.search('^list_action_([0-9]+)_([0-9]+)$', action)
				trigger = 'action'
			if len(match.groups()) != 2:
				return

			try:
				row = int(match.group(1))
				idx = int(match.group(2))
				if trigger == 'body':
					field = (await self.get_fields())[idx]
				else:
					field = (await self.get_actions())[idx]
				action = field['action']
				instance = self.objects[row]
			except Exception as e:
				logger.warning('Got invalid result in list item click: {}'.format(str(e)))
				return

			# Execute action/target method.
			if iscoroutinefunction(action):
				await action(player, values, instance, view=self)
			else:
				action(player, values, instance, view=self)

	@property
	def num_pages(self):
		return int(math.ceil(self.count / self.num_per_page))

	async def close(self, player, *args, **kwargs):
		"""
		Close the link for a specific player. Will hide manialink and destroy data for player specific to save memory.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		if self.player_data and player.login in self.player_data:
			del self.player_data[player.login]
		await self.hide(player_logins=[player.login])

	async def refresh(self, player, *args, **kwargs):
		"""
		Refresh list with current properties for a specific player. Can be used to show new data changes.

		:param player: Player model instance.
		:type player: pyplanet.apps.core.maniaplanet.models.Player
		"""
		await self.display(player=player)

	async def display(self, player=None):
		"""
		Display list to player.

		:param player: Player login or model instance.
		:type player: str, pyplanet.apps.core.maniaplanet.models.Player
		"""
		login = player.login if isinstance(player, Player) else player
		if not player:
			raise Exception('No player/login given to display the list to!')
		return await super().display(player_logins=[login])

	async def get_fields(self):
		return self.fields

	async def get_title(self):
		return self.title

	async def get_actions(self):
		return self.actions

	async def get_query(self):
		if self.query is not None:
			return self.query
		raise Exception('get_query() or self.query is empty! It should contain query that is not yet executed!')

	async def apply_filter(self, query):
		if not self.search_text:
			return query
		for field in self.fields:
			if 'searching' in field and field['searching']:
				query = query.orwhere(getattr(self.model, field['index']).contains(self.search_text))
		return query

	async def apply_ordering(self, query):
		if not self.order:
			return query
		return query.order_by(self.order)

	async def apply_pagination(self, query):
		# Get count before pagination.
		self.count = await self.model.objects.count(query)
		return query.paginate(self.page, self.num_per_page)

	async def get_object_data(self):
		query = await self.get_query()
		query = await self.apply_filter(query)
		query = await self.apply_ordering(query)
		query = await self.apply_pagination(query)
		self.objects = list(await self.model.execute(query))
		return {
			'objects': self.objects,
			'search': self.search_text,
			'order': self.order,
			'count': self.count,
		}

	async def get_context_data(self):
		context = await super().get_context_data()

		# Add dynamic data from query.
		context.update(await self.get_object_data())

		fields = await self.get_fields()
		actions = await self.get_actions()

		# Process fields + actions (normalize)
		# Calculate positions of fields
		left = 0
		for field in fields:
			field['left'] = left
			left += field['width']
			if 'type' not in field:
				field['type'] = 'label'
			if 'safe' not in field:
				field['safe'] = False

			field['_sort'] = None
			if self.sort_field is not None and field['index'] == self.sort_field['index']:
				field['_sort'] = self.sort_order
		fields_width = int(left)

		left = 0
		for action in actions:
			action['left'] = left
			left += action['width'] if 'width' in action else 5
			if 'type' not in action:
				action['type'] = 'quad'
			if 'safe' not in action:
				action['safe'] = False
		actions_width = int(left)

		# Add facts.
		context.update({
			'field_renderer': self._render_field,
			'fields': fields,
			'actions': actions,
			'provide_search': self.provide_search,
			'title': await self.get_title(),
			'icon_style': self.icon_style,
			'icon_substyle': self.icon_substyle,
			'search': self.search_text,
			'pages': self.num_pages,
			'page': self.page,
			'fields_width': fields_width,
			'actions_width': actions_width,
		})

		return context

	def _render_field(self, row, field):
		if 'renderer' in field:
			return field['renderer'](row, field)
		if isinstance(row, dict):
			return str(row[field['index']])
		else:
			return str(getattr(row, field['index']))

	async def _search(self, player, _, values, *args, **kwargs):
		search_text = values['list_search_field']
		if len(search_text) > 0 and search_text != 'Search...':
			self.search_text = search_text
		else:
			self.search_text = None
		# Reset page when searching
		self.page = 1
		await self.refresh(player)

	async def _first_page(self, player, *args, **kwargs):
		self.page = 1
		await self.refresh(player)

	async def _last_page(self, player, *args, **kwargs):
		self.page = self.num_pages
		await self.refresh(player)

	async def _next_page(self, player, *args, **kwargs):
		if self.page + 1 <= self.num_pages:
			self.page += 1
			await self.refresh(player)

	async def _next_10_pages(self, player, *args, **kwargs):
		if self.page + 10 <= self.num_pages:
			self.page += 10
			await self.refresh(player)

	async def _prev_page(self, player, *args, **kwargs):
		if self.page - 1 > 0:
			self.page -= 1
			await self.refresh(player)

	async def _prev_10_pages(self, player, *args, **kwargs):
		if self.page - 10 > 0:
			self.page -= 10
			await self.refresh(player)


class ManualListView(ListView):
	"""
	The ManualListView will act as a ListView, but not based on a model or query.
	"""

	def __init__(self, data=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.objects_raw = data

	async def get_data(self):
		"""
		Override this method, return a list with dictionaries inside.
		"""
		if not self.objects_raw:
			raise NotImplementedError
		return self.objects_raw

	async def get_object_data(self):
		frame = pd.DataFrame(await self.get_data())
		frame = await self.apply_filter(frame)
		frame = await self.apply_ordering(frame)
		self.count = len(frame)
		frame = await self.apply_pagination(frame)
		self.objects = frame.to_dict('records')
		return {
			'objects': self.objects,
			'search': self.search_text,
			'order': self.order,
			'count': self.count,
		}

	async def apply_filter(self, frame):
		if not self.search_text:
			return frame
		query = list()
		for field in await self.get_fields():
			if 'searching' in field and field['searching']:
				if 'search_strip_styles' in field and field['search_strip_styles']:
					query.append(
						frame[field['index']].apply(lambda x: self.search_text.lower() in style.style_strip(x.lower()))
					)
				else:
					query.append(
						frame[field['index']].apply(lambda x: self.search_text.lower() in x.lower())
					)
		if query:
			query = np.logical_or.reduce(query)
			return frame.loc[query]
		return frame

	async def apply_ordering(self, frame):
		if self.sort_field:
			return frame.sort_values(self.sort_field['index'], ascending=bool(self.sort_order))
		return frame

	async def apply_pagination(self, frame):
		return frame[(self.page - 1) * self.num_per_page:self.page * self.num_per_page]
