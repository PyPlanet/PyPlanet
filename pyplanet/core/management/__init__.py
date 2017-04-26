import asyncio
import functools
import pkgutil
import os
import sys

from collections import defaultdict
from importlib import import_module

from pyplanet import __version__ as version
from pyplanet.conf import settings
from pyplanet.core.exceptions import ImproperlyConfigured
from pyplanet.core.management.base import CommandParser, CommandError, handle_default_options, BaseCommand
from pyplanet.core.management.color import color_style


def find_commands(management_dir):
	command_dir = os.path.join(management_dir, 'commands')
	return [name for _, name, is_pkg in pkgutil.iter_modules([command_dir])]


@functools.lru_cache(maxsize=None)
def get_commands():
	"""
	Return a dictionary mapping command names to their callback applications.
	
	Look for a management.commands package in pyplanet.core, and in each
	installed application -- if a commands package exists, register all
	commands in that package.
	
	Core commands are always included. If a settings module has been
	specified, also include user-defined commands.
	
	The dictionary is in the format {command_name: app_name}. Key-value
	pairs from this dictionary can then be used in calls to
	load_command_class(app_name, command_name).
	
	If a specific version of a command must be loaded (e.g., with the
	startapp command), the instantiated module can be placed in the
	dictionary in place of the application name.
	
	The dictionary is cached on the first call and reused on subsequent
	calls.
	"""
	commands = {name: 'pyplanet.core' for name in find_commands(__path__[0])}

	if not settings.configured:
		return commands

	# TODO: Implement later.
	# for app_config in reversed(list(apps.get_app_configs())):
	# 	path = os.path.join(app_config.path, 'management')
	# 	commands.update({name: app_config.name for name in find_commands(path)})

	return commands


def load_command_class(app_name, name):
	"""
	Given a command name and an application name, return the Command
	class instance. Allow all errors raised by the import process
	(ImportError, AttributeError) to propagate.
	"""
	module = import_module('{}.management.commands.{}'.format(app_name, name))
	return module.Command()


class ManagementUtility:
	def __init__(self, argv):
		self.argv = argv or sys.argv[:]
		self.prog_name = os.path.basename(self.argv[0])
		self.version = version
		self.loop = asyncio.get_event_loop()
		self.settings_exception = None

		self.commands = find_commands(__path__[0])

	def fetch_command(self, subcommand):
		"""
		Try to fetch the given subcommand, printing a message with the 
		appropriate command called from the command line (usually "pyplanet" or "manage.py") if it can't be found.
		"""
		# Get commands outside of try block to prevent swallowing exceptions
		commands = get_commands()
		try:
			app_name = commands[subcommand]
		except KeyError:
			if os.environ.get('PYPLANET_SETTINGS_MODULE'):
				# If `subcommand` is missing due to misconfigured settings, the
				# following line will retrigger an ImproperlyConfigured exception
				# (get_commands() swallows the original one) so the user is
				# informed about it.
				_ = settings.APPS
			else:
				sys.stderr.write('No PyPlanet settings specified.\n')
			sys.stderr.write(
				'Unknown command: {}\nType \'{} help\' for usage.\n'.format(subcommand, self.prog_name)
			)
			sys.exit(1)
		if isinstance(app_name, BaseCommand):
			# If the command is already loaded, use it directly.
			klass = app_name
		else:
			klass = load_command_class(app_name, subcommand)
		return klass

	def execute(self):
		try:
			subcommand = self.argv[1]
		except:
			subcommand = 'help'

		# Root parser.
		parser = CommandParser(None, usage='%(prog)s subcommand [options] [args]', add_help=False)
		parser.add_argument('--settings')
		parser.add_argument('--pool')
		parser.add_argument('--pythonpath')
		parser.add_argument('args', nargs='*')
		try:
			options, args = parser.parse_known_args(self.argv[2:])
			handle_default_options(options)
		except CommandError:
			pass # Ignore any option errors at this point.

		try:
			settings.APPS
		except ImproperlyConfigured as e:
			self.settings_exception = e

		# TODO: Load some parts of the app (with the provided pool or default pool) so we can load commands from apps.

		self.autocomplete()

		if subcommand == 'help':
			if '--commands' in args:
				sys.stdout.write(self.main_help_text(commands_only=True) + '\n')
			elif len(options.args) < 1:
				sys.stdout.write(self.main_help_text() + '\n')
			else:
				self.fetch_command(options.args[0]).print_help(self.prog_name, options.args[0])
			# Special-cases: We want 'pyplanet --version' and
			# 'pyplanet --help' to work, for backwards compatibility.
		elif subcommand == 'version' or self.argv[1:] == ['--version']:
			sys.stdout.write(self.version + '\n')
		elif self.argv[1:] in (['--help'], ['-h']):
			sys.stdout.write(self.main_help_text() + '\n')
		else:
			self.fetch_command(subcommand).run_from_argv(self.argv)

	def main_help_text(self, commands_only=False):
		"""Return the script's main help text, as a string."""
		if commands_only:
			usage = sorted(get_commands().keys())
		else:
			usage = [
				"",
				"Type '{} help <subcommand>' for help on a specific subcommand.".format(self.prog_name),
				"",
				"Available subcommands:",
				]

			commands_dict = defaultdict(lambda: [])
			for name, app in get_commands().items():
				if app == 'pyplanet.core':
					app = 'pyplanet'
				else:
					app = app.rpartition('.')[-1]
				commands_dict[app].append(name)

			style = color_style()

			for app in sorted(commands_dict.keys()):
				usage.append("")
				usage.append(style.NOTICE("[{}]".format(app)))
				for name in sorted(commands_dict[app]):
					usage.append("    {}".format(name))

			# Output an extra note if settings are not properly configured
			if self.settings_exception is not None:
				usage.append(style.NOTICE(
					'\n'
					'Note that only PyPlanet core commands are listed '
					'as settings are not properly configured (error: {}).'.format(self.settings_exception)
				))

		return '\n'.join(usage)

	def autocomplete(self):
		"""
		Output completion suggestions for BASH.
		
		The output of this function is passed to BASH's `COMREPLY` variable and
		treated as completion suggestions. `COMREPLY` expects a space
		separated string as the result.
		
		The `COMP_WORDS` and `COMP_CWORD` BASH environment variables are used
		to get information about the cli input. Please refer to the BASH
		man-page for more information about this variables.
		
		Subcommand options are saved as pairs. A pair consists of
		the long option string (e.g. '--exclude') and a boolean
		value indicating if the option requires arguments. When printing to
		stdout, an equal sign is appended to options which require arguments.
		
		Note: If debugging this function, it is recommended to write the debug
		output in a separate file. Otherwise the debug output will be treated
		and formatted as potential completion suggestions.
		"""
		# Don't complete if user hasn't sourced bash_completion file.
		if 'PYPLANET_AUTO_COMPLETE' not in os.environ:
			return

		cwords = os.environ['COMP_WORDS'].split()[1:]
		cword = int(os.environ['COMP_CWORD'])

		try:
			curr = cwords[cword - 1]
		except IndexError:
			curr = ''

		subcommands = list(get_commands()) + ['help']
		options = [('--help', False)]

		# subcommand
		if cword == 1:
			print(' '.join(sorted(filter(lambda x: x.startswith(curr), subcommands))))
		# subcommand options
		# special case: the 'help' subcommand has no options
		elif cwords[0] in subcommands and cwords[0] != 'help':
			subcommand_cls = self.fetch_command(cwords[0])
			parser = subcommand_cls.create_parser('', cwords[0])
			options.extend(
				(min(s_opt.option_strings), s_opt.nargs != 0)
				for s_opt in parser._actions if s_opt.option_strings
			)
			# filter out previously specified options from available options
			prev_opts = {x.split('=')[0] for x in cwords[1:cword - 1]}
			options = (opt for opt in options if opt[0] not in prev_opts)

			# filter options by current input
			options = sorted((k, v) for k, v in options if k.startswith(curr))
			for opt_label, require_arg in options:
				# append '=' to options which require args
				if require_arg:
					opt_label += '='
				print(opt_label)
		# Exit code of the bash completion function is never passed back to
		# the user, so it's safe to always exit with 0.
		# For more details see #25420.
		sys.exit(0)


def execute_from_command_line(argv=None):
	"""Run a ManagementUtility."""
	utility = ManagementUtility(argv)
	utility.execute()
