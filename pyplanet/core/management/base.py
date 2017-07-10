import sys
import os

from io import TextIOBase
from argparse import ArgumentParser

from pyplanet import __version__ as version
from pyplanet.core import checks
from pyplanet.core.management.color import no_style, color_style


class CommandError(Exception):
	"""
	Exception class indicating a problem while executing a management
	command.
	If this exception is raised during the execution of a management
	command, it will be caught and turned into a nicely-printed error
	message to the appropriate output stream (i.e., stderr); as a
	result, raising this exception (with a sensible description of the
	error) is the preferred way to indicate that something has gone
	wrong in the execution of a command.
	"""
	pass


class SystemCheckError(CommandError):
	"""
	The system check framework detected unrecoverable errors.
	"""
	pass


class CommandParser(ArgumentParser):
	def __init__(self, cmd, **kwargs):
		self.cmd = cmd
		super().__init__(**kwargs)

	def parse_args(self, args=None, namespace=None):
		# Catch missing argument for a better error message
		if (hasattr(self.cmd, 'missing_args_message') and
				not (args or any(not arg.startswith('-') for arg in args))):
			self.error(self.cmd.missing_args_message)
		return super().parse_args(args, namespace)

	def error(self, message):
		if self.cmd._called_from_command_line:
			super().error(message)
		else:
			raise CommandError("Error: %s" % message)


def handle_default_options(options):
	"""
	Include any default options that all commands should accept here
	so that ManagementUtility can handle them before searching for
	user commands.
	"""
	if options.settings:
		os.environ['PYPLANET_SETTINGS_MODULE'] = options.settings
	if options.pythonpath:
		sys.path.insert(0, options.pythonpath)
	if options.pool:
		os.environ['PYPLANET_POOL'] = options.pool


class BaseCommand:
	"""
	The base class from which all management commands ultimately
	derive.

	Use this class if you want access to all of the mechanisms which
	parse the command-line arguments and work out what code to call in
	response; if you don't need to change any of that behavior,
	consider using one of the subclasses defined in this file.

	If you are interested in overriding/customizing various aspects of
	the command-parsing and -execution behavior, the normal flow works
	as follows:

	1. ``pyplanet`` or ``manage.py`` loads the command class
	   and calls its ``run_from_argv()`` method.

	2. The ``run_from_argv()`` method calls ``create_parser()`` to get
	   an ``ArgumentParser`` for the arguments, parses them, performs
	   any environment changes requested by options like
	   ``pythonpath``, and then calls the ``execute()`` method,
	   passing the parsed arguments.

	3. The ``execute()`` method attempts to carry out the command by
	   calling the ``handle()`` method with the parsed arguments; any
	   output produced by ``handle()`` will be printed to standard
	   output and, if the command is intended to produce a block of
	   SQL statements, will be wrapped in ``BEGIN`` and ``COMMIT``.

	4. If ``handle()`` or ``execute()`` raised any exception (e.g.
	   ``CommandError``), ``run_from_argv()`` will  instead print an error
	   message to ``stderr``.

	Thus, the ``handle()`` method is typically the starting point for
	subclasses; many built-in commands and command types either place
	all of their logic in ``handle()``, or perform some additional
	parsing work in ``handle()`` and then delegate from it to more
	specialized methods as needed.

	Several attributes affect behavior at various steps along the way:

	``help``
		A short description of the command, which will be printed in
		help messages.

	``output_transaction``
		A boolean indicating whether the command outputs SQL
		statements; if ``True``, the output will automatically be
		wrapped with ``BEGIN;`` and ``COMMIT;``. Default value is
		``False``. Not used right now, ignored!

	``requires_migrations_checks``
		A boolean; if ``True``, the command prints a warning if the set of
		migrations on disk don't match the migrations in the database.
		Not used currently, ignored!

	``requires_system_checks``
		A boolean; if ``True``, entire PyPlanet project will be checked for errors
		prior to executing the command. Default value is ``True``.
		To validate an individual application's models
		rather than all applications' models, call
		``self.check(app_configs)`` from ``handle()``, where ``app_configs``
		is the list of application's configuration provided by the
		app registry.

	``leave_locale_alone``
		A boolean indicating whether the locale set in settings should be
		preserved during the execution of the command instead of translations
		being deactivated.

		Default value is ``False``.

		Make sure you know what you are doing if you decide to change the value
		of this option in your custom command if it creates database content
		that is locale-sensitive and such content shouldn't contain any
		translations (like it happens e.g. with django.contrib.auth
		permissions) as activating any locale might cause unintended effects.
	"""
	# Metadata about this command.
	help = ''

	# Configuration shortcuts that alter various logic.
	_called_from_command_line = False
	output_transaction = False  # Whether to wrap the output in a "BEGIN; COMMIT;"
	leave_locale_alone = False
	requires_migrations_checks = False
	requires_system_checks = True

	# default arguments required
	arg_pool_required = False
	arg_settings_required = False

	def __init__(self, stdout=None, stderr=None, no_color=False):
		self.stdout = OutputWrapper(stdout or sys.stdout)
		self.stderr = OutputWrapper(stderr or sys.stderr)
		if no_color:
			self.style = no_style()
		else:
			self.style = color_style()
			self.stderr.style_func = self.style.ERROR

	def get_version(self):
		"""
		Return the PyPlanet version, which should be correct for all built-in
		PyPlanet commands. User-supplied commands can override this method to
		return their own version.
		"""
		return version

	def create_parser(self, prog_name, subcommand):
		"""
		Create and return the ``ArgumentParser`` which will be used to
		parse the arguments to this command.
		"""
		parser = CommandParser(
			self, prog='{} {}'.format(os.path.basename(prog_name), subcommand),
			description=self.help or None,
		)
		parser.add_argument('--version', action='version', version=self.get_version())
		parser.add_argument(
			'-v', '--verbosity', action='store', dest='verbosity', default=1,
			type=int, choices=[0, 1, 2, 3],
			help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output',
		)
		parser.add_argument(
			'--settings',
			help=(
				'The Python path to a settings module, e.g. '
				'"myproject.settings.main". If this isn\'t provided, the '
				'PYPLANET_SETTINGS_MODULE environment variable will be used.'
			),
		)
		parser.add_argument(
			'--pool',
			help=(
				'The PyPlanet pool to use when executing commands. '
				'If this isn\'t provided, the PYPLANET_POOL environment variable will be used.'
				'If the environment variable isn\'t provided, \'default\' will be used.'
			),
			required=self.arg_pool_required,
		)
		parser.add_argument(
			'--pythonpath',
			help='A directory to add to the Python path, e.g. "/home/pyplanetprojects/myproject".',
		)
		parser.add_argument('--traceback', action='store_true', help='Raise on CommandError exceptions')
		parser.add_argument(
			'--no-color', action='store_true', dest='no_color',
			help='Don\'t colorize the command output.',
		)
		self.add_arguments(parser)
		return parser

	def add_arguments(self, parser):
		"""
		Entry point for subclassed commands to add custom arguments.
		:param parser: Parser instance
		:type parser: argparse.ArgumentParser
		"""
		pass

	def print_help(self, prog_name, subcommand):
		"""
		Print the help message for this command, derived from
		``self.usage()``.
		"""
		parser = self.create_parser(prog_name, subcommand)
		parser.print_help()

	def run_from_argv(self, argv):
		"""
		Set up any environment changes requested (e.g., Python path
		and PyPlanet settings), then run this command. If the
		command raises a ``CommandError``, intercept it and print it sensibly
		to stderr. If the ``--traceback`` option is present or the raised
		``Exception`` is not ``CommandError``, raise it.
		"""
		self._called_from_command_line = True
		parser = self.create_parser(argv[0], argv[1])

		options = parser.parse_args(argv[2:])
		cmd_options = vars(options)
		# Move positional args out of options to mimic legacy optparse
		args = cmd_options.pop('args', ())
		handle_default_options(options)
		try:
			self.execute(*args, **cmd_options)
		except Exception as e:
			if options.traceback or not isinstance(e, CommandError):
				raise

			# SystemCheckError takes care of its own formatting.
			if isinstance(e, SystemCheckError):
				self.stderr.write(str(e), lambda x: x)
			else:
				self.stderr.write('{}: {}'.format(e.__class__.__name__, e))
			sys.exit(1)
		finally:
			pass
			# TODO: Close all db connections etc.

	def execute(self, *args, **options):
		"""
		Try to execute this command, performing system checks if needed (as
		controlled by the ``requires_system_checks`` attribute, except if
		force-skipped).
		"""
		if options['no_color']:
			self.style = no_style()
			self.stderr.style_func = None
		if options.get('stdout'):
			self.stdout = OutputWrapper(options['stdout'])
		if options.get('stderr'):
			self.stderr = OutputWrapper(options['stderr'], self.stderr.style_func)

		try:
			if self.requires_system_checks and not options.get('skip_checks'):
				self.check()
			if self.requires_migrations_checks:
				self.check_migrations()
			output = self.handle(*args, **options)
			if output:
				# TODO: Output transactions if self.output_transaction is given!
				self.stdout.write(output)
		finally:
			pass
		return output

	def _run_checks(self, **kwargs):
		return checks.run_checks(**kwargs)

	def check(self, app_configs=None, tags=None, display_num_errors=False,
			  include_deployment_checks=False, fail_level=checks.ERROR):
		"""
		Use the system check framework to validate entire PyPlanet project.
		Raise CommandError for any serious message (error or critical errors).
		If there are only light messages (like warnings), print them to stderr
		and don't raise an exception.
		"""
		all_issues = self._run_checks(
			app_configs=app_configs,
			tags=tags,
			include_deployment_checks=include_deployment_checks,
		)

		header, body, footer = '', '', ''
		visible_issue_count = 0  # excludes silenced warnings

		if all_issues:
			debugs = [e for e in all_issues if e.level < checks.INFO and not e.is_silenced()]
			infos = [e for e in all_issues if checks.INFO <= e.level < checks.WARNING and not e.is_silenced()]
			warnings = [e for e in all_issues if checks.WARNING <= e.level < checks.ERROR and not e.is_silenced()]
			errors = [e for e in all_issues if checks.ERROR <= e.level < checks.CRITICAL and not e.is_silenced()]
			criticals = [e for e in all_issues if checks.CRITICAL <= e.level and not e.is_silenced()]
			sorted_issues = [
				(criticals, 'CRITICALS'),
				(errors, 'ERRORS'),
				(warnings, 'WARNINGS'),
				(infos, 'INFOS'),
				(debugs, 'DEBUGS'),
			]

			for issues, group_name in sorted_issues:
				if issues:
					visible_issue_count += len(issues)
					formatted = (
						self.style.ERROR(str(e))
						if e.is_serious()
						else self.style.WARNING(str(e))
						for e in issues)
					formatted = '\n'.join(sorted(formatted))
					body += '\n{}:\n{}\n'.format(group_name, formatted)

		if visible_issue_count:
			header = 'System check identified some issues:\n'

		if display_num_errors:
			if visible_issue_count:
				footer += '\n'
			footer += 'System check identified {} ({} silenced).'.format(
				'no issues' if visible_issue_count == 0 else
				'1 issue' if visible_issue_count == 1 else
				'%s issues' % visible_issue_count,
				len(all_issues) - visible_issue_count,
			)

		if any(e.is_serious(fail_level) and not e.is_silenced() for e in all_issues):
			msg = self.style.ERROR('SystemCheckError: {}'.format(header)) + body + footer
			raise SystemCheckError(msg)
		else:
			msg = header + body + footer

		if msg:
			if visible_issue_count:
				self.stderr.write(msg, lambda x: x)
			else:
				self.stdout.write(msg)

	def check_migrations(self):
		"""
		Print a warning if the set of migrations on disk don't match the
		migrations in the database.
		"""
		# TODO: Check for migrations. Not yet provided in the cli.
		return

	def handle(self, *args, **options):
		"""
		The actual logic of the command. Subclasses must implement
		this method.
		"""
		raise NotImplementedError('subclasses of BaseCommand must provide a handle() method')


class AppCommand(BaseCommand):
	"""
	A management command which takes one or more installed application labels
	as arguments, and does something with each of them.

	Rather than implementing ``handle()``, subclasses must implement
	``handle_app_config()``, which will be called once for each application.
	"""
	missing_args_message = "Enter at least one application label."

	def add_arguments(self, parser):
		parser.add_argument('args', metavar='app_label', nargs='+', help='One or more application label.')

	def handle(self, *app_labels, **options):
		# TODO: Implement
		return

	def handle_app_config(self, app_config, **options):
		"""
		Perform the command's actions for app_config, an AppConfig instance
		corresponding to an application label given on the command line.
		"""
		raise NotImplementedError(
			"Subclasses of AppCommand must provide"
			"a handle_app_config() method.")


class LabelCommand(BaseCommand):
	"""
	A management command which takes one or more arbitrary arguments
	(labels) on the command line, and does something with each of
	them.

	Rather than implementing ``handle()``, subclasses must implement
	``handle_label()``, which will be called once for each label.

	If the arguments should be names of installed applications, use
	``AppCommand`` instead.
	"""
	label = 'label'
	missing_args_message = 'Enter at least one {}.'.format(label)

	def add_arguments(self, parser):
		parser.add_argument('args', metavar=self.label, nargs='+')

	def handle(self, *labels, **options):
		output = []
		for label in labels:
			label_output = self.handle_label(label, **options)
			if label_output:
				output.append(label_output)
		return '\n'.join(output)

	def handle_label(self, label, **options):
		"""
		Perform the command's actions for ``label``, which will be the
		string as given on the command line.
		"""
		raise NotImplementedError('subclasses of LabelCommand must provide a handle_label() method')


class OutputWrapper(TextIOBase):
	"""
	Wrapper around stdout/stderr
	"""
	@property
	def style_func(self):
		return self._style_func

	@style_func.setter
	def style_func(self, style_func):
		if style_func and self.isatty():
			self._style_func = style_func
		else:
			self._style_func = lambda x: x

	def __init__(self, out, style_func=None, ending='\n'):
		self._out = out
		self.style_func = None
		self.ending = ending

	def __getattr__(self, name):
		return getattr(self._out, name)

	def isatty(self):
		return hasattr(self._out, 'isatty') and self._out.isatty()

	def write(self, msg, style_func=None, ending=None):
		ending = self.ending if ending is None else ending
		if ending and not msg.endswith(ending):
			msg += ending
		style_func = style_func or self.style_func
		self._out.write(style_func(msg))
