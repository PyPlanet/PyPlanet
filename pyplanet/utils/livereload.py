from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class LiveReload(FileSystemEventHandler):
	def __init__(self, pool):
		"""
		:param pool:
		:type pool: pyplanet.god.pool.EnvironmentPool
		"""
		self.pool = pool

	def on_any_event(self, event):
		if isinstance(event, FileModifiedEvent):
			if event.src_path.endswith('.py'):
				self.pool.restart()

