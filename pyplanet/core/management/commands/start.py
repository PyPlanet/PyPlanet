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
from pyplanet.god.pool import EnvironmentPool
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

		self.pool = None

	def add_arguments(self, parser):
		parser.add_argument('--max-restarts', type=int, default=0)
		parser.add_argument('--tokio', dest='tokio', action='store_true')
		parser.add_argument('--detach', dest='detach', action='store_true')
		parser.add_argument('--pid-file', type=str, default=None)

	def handle(self, *args, **options):
		# Detach when asked.
		if 'detach' in options and options['detach']:
			self.detach(pid_file=options['pid_file'] if 'pid_file' in options and options['pid_file'] else 'pyplanet.pid')

		# Initiate the logger.
		threading.current_thread().setName('Main')
		initiate_logger()
		logger = logging.getLogger(__name__)

		# Initiate the settings by accessing one.
		logger.debug('Initiated configuration and environment... (debug on, means no error reporting and verbose output')
		if not settings.DEBUG:
			logger.info('Initiated configuration and environment...')
		logger.info('-------------------------------[  PyPlanet v{}  ]-------------------------------'.format(self.get_version()))

		# Start god process (the current started process).
		self.pool = EnvironmentPool(settings.POOLS, max_restarts=options['max_restarts'], options=options)
		self.pool.populate()

		# Starting all processes.
		self.pool.start()

		# Start the watchdog.
		try:
			self.pool.watchdog()
		except KeyboardInterrupt:
			self.pool.shutdown()
			exit(0)

	def detach(self, pid_file):
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

		# Try to get lock on the file.
		try:
			fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
		except IOError:
			logging.error('Can\'t create PID file! Can\'t lock on file!')

			# We need to overwrite the pidfile if we got here.
			with open(pid_file, 'w') as pid_handle:
				pid_handle.write(old_pid)

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

		# Write PID file.
		lock_file.write(str(os.getpid()))
		lock_file.flush()

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
