import os
import signal
import threading
import logging
import sys
import atexit

try:
	import fcntl
except:
	fcntl = dict()  # Windows only.

from pyplanet.conf import settings
from pyplanet.core.management import BaseCommand
from pyplanet.utils.log import initiate_logger


class Command(BaseCommand):  # pragma: no cover
	help = 'Start the PyPlanet god with all it\'s subprocesses.'

	requires_system_checks = False
	requires_migrations_checks = False

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.detached = False
		self.pid_file = None
		self.pid = None
		self.env_path = None

		self.pool = None

	def add_arguments(self, parser):
		parser.add_argument('--max-restarts', type=int, default=0)
		parser.add_argument('--tokio', dest='tokio', action='store_true')
		parser.add_argument('--detach', dest='detach', action='store_true')
		parser.add_argument('--pid-file', type=str, default=None)
		parser.add_argument('--env', type=str, default=None, help='ENV file path')

	def handle(self, *args, **options):
		# Detach when asked.
		if 'detach' in options and options['detach']:
			self.detach()

		# Write process ID (pid) to file.
		self.write_pid(pid_file=options['pid_file'] if 'pid_file' in options and options['pid_file'] else 'pyplanet.pid')

		# Verify env path.
		if options['env']:
			if os.path.exists(options['env']) and os.path.isfile(options['env']):
				os.environ['PYPLANET_ENV_PATH'] = options['env']

		# Initiate the logger.
		threading.current_thread().setName('Main')
		initiate_logger()
		logger = logging.getLogger(__name__)

		# Initiate the settings by accessing one.
		logger.debug('Initiated configuration and environment... (debug on, means no error reporting and verbose output')
		if not settings.PYPLANET_DEBUG:
			logger.info('Initiated configuration and environment...')
		logger.info('-------------------------------[  PyPlanet v{}  ]-------------------------------'.format(self.get_version()))

		# Start PyPlanet.
		from pyplanet.core.instance import Controller

		# Tokio Asyncio (EXPERIMENTAL).
		if 'tokio' in options and options['tokio'] is True:
			import asyncio
			import tokio
			policy = tokio.TokioLoopPolicy()
			asyncio.set_event_loop_policy(policy)
			asyncio.set_event_loop(tokio.new_event_loop())
			logging.warning('Using experimental Tokio Asyncio Loop!')

		# Try to activate UVLoop
		try:
			import uvloop
			uvloop.install()
			logging.info('Activated uvloop support.')
		except:
			pass

		# Initiate instance.
		instance = Controller.prepare().instance
		instance.start()

	def write_pid(self, pid_file):
		self.pid_file = pid_file

		# Check for old pid file.
		old_pid = ''
		if os.path.isfile(pid_file):
			with open(pid_file, 'r') as pid_handle:
				old_pid = pid_handle.read()

		# Create lock file.
		try:
			lock_file = open(pid_file, 'w')
		except IOError:
			logging.error('Can\'t create PID file!')
			sys.exit(1)

		# Try to get lock on the file (on non-Windows).
		if fcntl != dict():
			try:
				fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
			except IOError:
				logging.error('Can\'t create PID file! Can\'t lock on file!')

				# We need to overwrite the pidfile if we got here.
				with open(pid_file, 'w') as pid_handle:
					pid_handle.write(old_pid)

		# Write PID file.
		lock_file.write(str(os.getpid()))
		lock_file.flush()

	def detach(self):
		# Fork to background.
		try:
			pid = os.fork()
		except OSError as e:
			logging.error('Unable to fork, error: {} ({})'.format(str(e), e.errno))
			sys.exit(1)

		if pid != 0:
			# This is the parent process. Exit.
			os._exit(0)

		# Stop listening for signals.
		os.setsid()
		self.pid = os.getpid()

		# Determinate /dev/null on machine.
		dev_null = '/dev/null'
		if hasattr(os, 'devnull'):
			dev_null = os.devnull

		# Redirect output to dev null.
		dev_null_fd = os.open(dev_null, os.O_RDWR)
		os.dup2(dev_null_fd, 0)
		os.dup2(dev_null_fd, 1)
		os.dup2(dev_null_fd, 2)
		os.close(dev_null_fd)

		self.detached = True

		# Register shutdown methods.
		signal.signal(signal.SIGTERM, self.sigterm)
		signal.signal(signal.SIGHUP, self.sigterm)
		atexit.register(self.exit)

	def sigterm(self, signum, frame):
		self.pool.shutdown()
		sys.exit(0)

	def exit(self):
		os.remove(self.pid_file)
