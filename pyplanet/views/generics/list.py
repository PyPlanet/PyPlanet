import math
import re
import logging

from asyncio import iscoroutinefunction

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.views.template import TemplateView

logger = logging.getLogger(__name__)


class ListView(TemplateView):
	query = None
	model = None

	title = None
	fields = []
	actions = []

	template_package = 'pyplanet.views'
	template_name = 'generics/list.xml'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.search_text = None
		self.sort_field = None
		self.sort_order = 1
		self.page = 1
		self.count = 0
		self.objects = list()

		self.num_per_page = 17

		self.provide_search = True

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
		if self.sort_order and self.sort_field:
			return self.sort_field
		elif not self.sort_order and self.sort_field:
			return -self.sort_field
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
				logger.warning('Got invalid result in list column click: {}'.format(str(e)))
				return

			# Check if sorting is defined + true.
			if 'sorting' not in field or not field['sorting'] or not field['index']:
				return

			# Sort on column
			model_field = getattr(self.model, field['index'])
			if self.sort_field and self.sort_field.db_column == model_field.db_column:
				if self.sort_order == 1:
					self.sort_order = 0
				else:
					# Unsort. clear sorting
					self.sort_field = None
					self.sort_order = 0
			else:
				self.sort_field = model_field
				self.sort_order = 1

			# Set sort state on field.
			for cur_field in fields:
				cur_field['_sort'] = None
			if self.sort_field:
				field['_sort'] = self.sort_order

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
				await action(player, values, instance)
			else:
				action(player, values, instance)

	@property
	def num_pages(self):
		return int(math.ceil(self.count / self.num_per_page))

	async def close(self, player, *args, **kwargs):
		self.data = None
		await self.hide(player_logins=[player.login])

	async def refresh(self, player, *args, **kwargs):
		await self.display(player=player)

	async def display(self, player=None):
		login = player.login if isinstance(player, Player) else player
		if not player:
			raise Exception('No player/login given to display the list to!')
		return await super().display(player_logins=[login])

	async def get_fields(self):
		return self.fields

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

		# Add facts.
		context.update({
			'field_renderer': self._render_field,
			'fields': fields,
			'actions': actions,
			'provide_search': self.provide_search,
			'title': self.title,
			'search': self.search_text,
			'pages': self.num_pages,
			'page': self.page,
		})

		return context

	def _render_field(self, row, field):
		if 'renderer' in field:
			return field['renderer'](row, field)
		return str(getattr(row, field['index']))

	async def _search(self, player, _, values, *args, **kwargs):
		search_text = values[0]['Value']
		if len(search_text) > 0 and search_text != 'Search...':
			self.search_text = search_text
		else:
			self.search_text = None
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
