import math

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.views.template import TemplateView


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
		self.search = None
		self.order = 'pk'
		self.page = 1
		self.count = 0

		self.num_per_page = 17

		self.provide_search = True

		# Setup the receivers.
		self.subscribe('list_button_close', self.close)
		self.subscribe('list_button_refresh', self.refresh)

	@property
	def num_pages(self):
		return math.ceil(self.count / self.num_per_page)

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
		# Calculate positions of fields
		left = 0
		for field in self.fields:
			field['left'] = left
			left += field['width']

		return self.fields

	async def get_actions(self):
		return self.actions

	async def get_query(self):
		if self.query is not None:
			return self.query
		raise Exception('get_query() or self.query is empty! It should contain query that is not yet executed!')

	async def apply_filter(self, query):
		return query

	async def apply_ordering(self, query):
		return query

	async def apply_pagination(self, query):
		# Get count before pagination.
		self.count = await self.model.objects.count(query)
		return query.paginate(self.page, self.num_per_page)

	async def get_object_data(self):
		query = await self.get_query()
		query = await self.apply_filter(query)
		query = await self.apply_ordering(query)
		query = await self.apply_pagination(query)
		return {
			'objects': list(await self.model.execute(query)),
			'search': self.search,
			'order': self.order,
		}

	async def get_context_data(self):
		context = await super().get_context_data()

		# Add dynamic data from query.
		context.update(await self.get_object_data())

		# Add facts.
		context.update({
			'field_renderer': self.render_field,
			'fields': await self.get_fields(),
			'provide_search': self.provide_search,
			'title': self.title,
			'search': self.search,
			'pages': self.num_pages,
			'page': self.page,
		})

		return context

	def render_field(self, row, field):
		if 'renderer' in field:
			return field['renderer'](row, field)
		return str(getattr(row, field['index']))
