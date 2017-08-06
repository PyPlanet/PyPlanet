from .base import StatsView


class TopRecordsView(StatsView):
	template_name = 'core.statistics/menu.xml'

	async def get_context_data(self):
		context = await super().get_context_data()
		context['options'] = [
			dict(name='Top Records', view='pyplanet.apps.core.statistics.views.records.TopRecords'),
		]
