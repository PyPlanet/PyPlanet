from pyplanet.views.generics.widget import TemplateView


class GearView(TemplateView):
	template_name = 'viewgear/gear.xml'

	def __init__(self, app, *args, **kwargs):
		super().__init__(app.context.ui, *args, **kwargs)
		self.app = app
		self.manager = app.context.ui
		self.id = 'view_gear'
