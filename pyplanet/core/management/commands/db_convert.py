from getpass import getpass

from pyplanet.contrib.converter import get_converter
from pyplanet.core import Controller
from pyplanet.core.management import BaseCommand


class Command(BaseCommand):
	help = 'Convert the database from XAseco2, eXpansion and other formats to PyPlanet.'

	requires_migrations_checks = True
	requires_system_checks = True

	arg_pool_required = True
	arg_settings_required = True

	def add_arguments(self, parser):
		parser.add_argument(
			'--source-format', required=True, help='The source format/controller type.',
			choices=['xaseco2', 'expansion'],
		)
		parser.add_argument(
			'--source-db-type', default='mysql', help='The source database type.',
			choices=['mysql'],
		)
		parser.add_argument('--source-db-username', help='Source database username.', required=True)
		parser.add_argument('--source-db-host', help='Source database hostname.', default='localhost')
		parser.add_argument('--source-db-name', help='Source database name (schema/database)', required=True)
		parser.add_argument('--source-db-port', help='Source database port, leave empty for the default one', default=None)
		parser.add_argument('--source-db-password', help='Source database password. Leave empty for asking', default=None)

	def handle(self, *args, **options):
		if options['source_db_password'] is None:
			options['source_db_password'] = getpass('Database Password: ')

		instance = Controller.prepare(options['pool']).instance
		converter = get_converter(
			options['source_format'], instance=instance, db_name=options['source_db_name'],
			db_type=options['source_db_type'], db_user=options['source_db_username'],
			db_port=options['source_db_port'], db_password=options['source_db_password'],
			db_host=options['source_db_host'],
		)

		instance.loop.run_until_complete(self.convert(instance, converter))

	async def convert(self, instance, converter):
		await converter.connect()
		await converter.start()
