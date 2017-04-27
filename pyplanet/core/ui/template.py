from jinja2 import Environment, PackageLoader, select_autoescape


async def load_template(package, file):
	return Template(package, file)


class Template:
	def __init__(self, package, file):

		self.file = file
		self.env = Environment(
			loader=PackageLoader(package, 'templates'),
			autoescape=select_autoescape(['html', 'xml', 'Txt', 'txt', 'ml', 'ms', 'script.txt', 'Script.Txt']),
		)
		self.template = self.env.get_template(file)

	async def render(self, **data):
		return self.template.render(**data)
