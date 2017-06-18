from importlib import import_module

from pyplanet.core.management import CommandError
from pyplanet.core.management.templates import TemplateCommand


class Command(TemplateCommand):
	help = 'Create a new PyPlanet local setup.'

	requires_system_checks = False
	requires_migrations_checks = False

	def handle(self, **options):
		project_name, target = options.pop('name'), options.pop('directory')
		self.validate_name(project_name, 'project')

		# Check that the project_name cannot be imported.
		try:
			if project_name == '.':
				raise ImportError()
			import_module(project_name)
		except ImportError:
			pass
		else:
			raise CommandError(
				"%r conflicts with the name of an existing Python module and "
				"cannot be used as a project name. Please try another name." % project_name
			)

		super().handle('project', project_name, target, **options)
