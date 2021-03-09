from pyplanet.views import TemplateView
from pyplanet.views.generics.widget import WidgetView


class SectorTimesWidget(WidgetView):
	# widget_x = 20
	widget_y = -70

	template_name = 'sector_times/sector_times.xml'

	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.sector_times.SectorTimes
		"""
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_sector_times'

	@property
	def widget_x(self):
		if self.app:
			if self.app.instance.game.game == 'tmnext':
				return -55
		return 20

	async def get_per_player_data(self, login):
		dedi_score = 0
		dedi_record = None
		local_score = 0
		local_record = None
		if 'dedimania' in self.app.instance.apps.apps:
			try:
				dedi_record = [x for x in self.app.instance.apps.apps['dedimania'].current_records if x.login == login]
				if len(dedi_record) > 0:
					dedi_record = dedi_record[0]
			except:
				pass
		if 'local_records' in self.app.instance.apps.apps:
			try:
				local_record = [x for x in self.app.instance.apps.apps['local_records'].current_records if x.player.login == login]
				if len(local_record) > 0:
					local_record = local_record[0]
			except:
				pass

		if dedi_record and hasattr(dedi_record, 'score'):
			dedi_score = dedi_record.score
		if local_record and hasattr(local_record, 'score'):
			local_score = local_record.score

		# Get fastest score, source and checkpoint scores.
		fastest_score = 0
		fastest_source = ''
		fastest_cps = list()
		if dedi_score > 0 and (local_score <= 0 or dedi_score < local_score):
			fastest_score = dedi_score
			fastest_cps = dedi_record.cps
			fastest_source = 'Dedi'
		elif local_score > 0 and (dedi_score <= 0 or local_score <= dedi_score):
			fastest_score = local_score
			fastest_cps = local_record.checkpoints
			fastest_source = 'Local'

		if isinstance(fastest_cps, list):
			fastest_cps = ','.join([str(c) for c in fastest_cps])

		context = await super().get_per_player_data(login)
		context['record_sector_times'] = fastest_cps
		context['record_time'] = fastest_score
		context['record_source'] = fastest_source
		if not fastest_cps:
			context['record_time'] = 0

		return context


class CheckpointDiffWidget(WidgetView):
	widget_x = 0
	widget_y = 0

	template_name = 'sector_times/cp_diff.xml'

	def __init__(self, app):
		"""
		:param app: App instance.
		:type app: pyplanet.apps.contrib.sector_times.SectorTimes
		"""
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.id = 'pyplanet__widgets_cp_diff'

	async def get_per_player_data(self, login):
		dedi_score = 0
		dedi_record = None
		local_score = 0
		local_record = None
		if 'dedimania' in self.app.instance.apps.apps:
			try:
				dedi_record = [x for x in self.app.instance.apps.apps['dedimania'].current_records if x.login == login]
				if len(dedi_record) > 0:
					dedi_record = dedi_record[0]
			except:
				pass
		if 'local_records' in self.app.instance.apps.apps:
			try:
				local_record = [x for x in self.app.instance.apps.apps['local_records'].current_records if x.player.login == login]
				if len(local_record) > 0:
					local_record = local_record[0]
			except:
				pass

		if dedi_record and hasattr(dedi_record, 'score'):
			dedi_score = dedi_record.score
		if local_record and hasattr(local_record, 'score'):
			local_score = local_record.score

		# Get fastest score, source and checkpoint scores.
		fastest_score = 0
		fastest_source = 'PB'
		fastest_cps = list()
		if dedi_score > 0 and (local_score <= 0 or dedi_score < local_score):
			fastest_score = dedi_score
			fastest_cps = dedi_record.cps
		elif local_score > 0 and (dedi_score <= 0 or local_score <= dedi_score):
			fastest_score = local_score
			fastest_cps = local_record.checkpoints

		if isinstance(fastest_cps, list):
			fastest_cps = ','.join([str(c) for c in fastest_cps])

		context = await super().get_per_player_data(login)
		context['record_sector_times'] = fastest_cps
		context['record_time'] = fastest_score
		context['record_source'] = fastest_source
		if not fastest_cps:
			context['record_time'] = 0

		return context


class GearIndicatorView(TemplateView):
	template_name = 'sector_times/gear_indicator.xml'

	def __init__(self, app, *args, **kwargs):
		super().__init__(app.context.ui, *args, **kwargs)
		self.app = app
		self.manager = app.context.ui
		self.id = 'sector_times_gear'
