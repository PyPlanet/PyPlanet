from pyplanet.utils.pip import Pip
from pyplanet.core.management import BaseCommand


class Command(BaseCommand):  # pragma: no cover
	help = 'Upgrade PyPlanet within the current PIP environment.'

	requires_system_checks = False
	requires_migrations_checks = False

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.pip = Pip()

	def add_arguments(self, parser):
		parser.add_argument(
			'--to-version', type=str, default=None,
			help='Upgrade to specific version given, leave empty to upgrade to latest'
		)

	def handle(self, *args, **options):
		version = options.get('to_version', None)
		print(options)

		if self.pip.is_supported:
			print('PIP: Found pip command: {}'.format(self.pip.command))
			print('PIP: ==> Supported!')
		else:
			print('PIP: ==>! Unsupported! Please manually upgrade your installation.')
			return

		print('')
		print('===================================================================================')
		print('! WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING WARNING !')
		print('The automatic update system can be unstable and can result in a broken installation')
		print('When the installation of PyPlanet is broken you have to use the manuals on the site')
		print('http://pypla.net')
		print('===================================================================================')

		user = input('Are you sure you want to upgrade PyPlanet to version: \'{}\'? [y/N]: '.format(
			version or 'latest'
		))
		if not user or not (user.lower() == 'y' or user.lower() == 'yes'):
			print('Cancelled!')
			return

		code, out, err = self.pip.install('pyplanet', target_version=version)

		if code == 0:
			print('Upgrade complete!')
		else:
			print('Error from PIP:')
			print(err.decode())
