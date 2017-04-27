import asyncio
import gc
import logging

from pyplanet.utils import log

logger = logging.getLogger(__name__)


class _LeakChecker:
	def __init__(self):
		self.reported = False

	def start(self):
		asyncio.get_event_loop().call_later(5, self.check_memory_leak)

	def check_memory_leak(self):
		asyncio.get_event_loop().call_later(30, self.check_memory_leak)
		logger.debug('Checking for memory leaks...')
		if 0 < len(gc.garbage) < 20:
			logger.warning('Found possible memory leaks: {}'.format(gc.garbage))
		elif len(gc.garbage) >= 20:
			logger.error(
				'Found memory leaks: {}'.format(gc.garbage)
			)
			if not self.reported:
				try:
					raise MemoryError('Found memory leaks: {}'.format(gc.garbage))
				except MemoryError as e:
					log.handle_exception(exception=e, extra_data=dict(leaks=gc.garbage))
				self.reported = True


checker = _LeakChecker()
