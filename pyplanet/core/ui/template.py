from jinja2 import Environment, PackageLoader, select_autoescape

from pyplanet.core.ui.loader import PyPlanetLoader


async def load_template(file):
	return Template(file)


class Template:
	def __init__(self, file):

		self.file = file
		self.env = Environment(
			loader=PyPlanetLoader.get_loader(),
			autoescape=select_autoescape(['html', 'xml', 'Txt', 'txt', 'ml', 'ms', 'script.txt', 'Script.Txt']),
		)
		self.template = self.env.get_template(file)

	async def render(self, **data):
		return self.template.render(**data)
