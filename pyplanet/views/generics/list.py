from pyplanet.views.template import TemplateView


class ListView(TemplateView):
	query = None
	model = None
	fields = []
	actions = []

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.search = None
		self.order = 'pk'
		self.page = 1
		self.count = 0

	async def get_fields(self):
		return self.fields

	async def get_actions(self):
		return self.actions

	async def get_query(self):
		if self.query:
			return self.query
		raise Exception('get_query() or self.query is empty! It should contain query that is not yet executed!')

	async def apply_filter(self, query):
		return query

	async def apply_ordering(self, query):
		return query

	async def apply_pagination(self, query):
		# Get count before pagination.
		self.count = await self.model.execute(query.count())
		return query.paginate(self.page, 20)

	async def get_object_data(self):
		query = await self.get_query()
		query = await self.apply_filter(query)
		query = await self.apply_ordering(query)
		query = await self.apply_pagination(query)
		return {
			'object': list(await self.model.execute(query)),
			'search': self.search,
			'order': self.order,
			'page': self.page,
		}

	async def get_context_data(self):
		context = await super().get_context_data()
		context.update(await self.get_object_data())
		return context
