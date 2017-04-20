from pyplanet.views.template import TemplateView


class TableView(TemplateView):
	query = None
	fields = []

	def get_fields(self):
		return self.fields

	async def get_object_data(self):
		pass

	async def get_context_data(self):
		context = super().get_context_data()
		context.update(await self.get_object_data())
		return context
