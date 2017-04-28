import os

from jinja2 import PrefixLoader, FileSystemLoader, PackageLoader


class _PyPlanetLoader(PrefixLoader):

	def __init__(self, mapping=None, delimiter='/'):
		super().__init__(mapping=mapping or self.get_mapping(), delimiter=delimiter)

	@classmethod
	def get_mapping(cls):
		from pyplanet.core import Controller

		mapping = dict()

		# Static core components.
		mapping['core.views'] = PackageLoader('pyplanet.views', 'templates')

		# Add app prefixes.
		for app_label, app in Controller.instance.apps.apps.items():
			template_path = os.path.join(app.path, 'templates')
			if os.path.exists(template_path):
				mapping[app_label] = FileSystemLoader(template_path)

		return mapping


class PyPlanetLoader:
	"""
	Lazy loader for the pyplanet jinja2 loader.
	"""
	_INSTANCE = None

	@classmethod
	def get_loader(cls):
		if not cls._INSTANCE:
			cls._INSTANCE = _PyPlanetLoader()
		return cls._INSTANCE
