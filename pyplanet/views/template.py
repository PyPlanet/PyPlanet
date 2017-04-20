from pyplanet.core.ui.template import load_template
from pyplanet.views.base import View


class TemplateView(View):
	template_package = None
	template_name = None

	async def get_context_data(self):
		"""
		Get global and local context data, used to render template.
		"""
		context = dict(
			# TODO: Global context.
		)
		return context

	async def get_player_data(self):
		"""
		Get data per player, return dict with login => data dict.
		"""
		return dict()

	async def get_template(self):
		return load_template(self.template_package, self.template_name)

	async def render(self, *args, player_login=None, **kwargs):
		"""
		:inherit: 
		"""
		kwargs['data'] = await self.get_context_data()
		kwargs['player_data'] = await self.get_player_data()
		kwargs['template'] = await self.get_template()
		super().render(*args, **kwargs)
