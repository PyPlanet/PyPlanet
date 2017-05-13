from importlib import import_module

from pyplanet.core.management import CommandError
from pyplanet.core.management.templates import TemplateCommand


class Command(TemplateCommand):
	help = 'Create a new app in your local apps. package. You should consider moving it up once you want to publish it!'

	requires_system_checks = False
	requires_migrations_checks = False

	template_files = [
		'__init__.py',
		'models.py',
	]

	def handle(self, **options):
		app_name, target = options.pop('name'), options.pop('directory')
		self.validate_name(app_name, 'app')

		# Check that the app_name cannot be imported.
		try:
			import_module(app_name)
		except ImportError:
			pass
		else:
			raise CommandError(
				"%r conflicts with the name of an existing Python module and "
				"cannot be used as an app name. Please try another name." % app_name
			)

		super().handle('app', app_name, target, **options)
