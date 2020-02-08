import json
import os

from pyplanet.conf.backends.file import FileConfigBackend
from pyplanet.core.exceptions import ImproperlyConfigured


class JsonConfigBackend(FileConfigBackend):
	name = 'json'
	files = ['base.json', 'apps.json']
	required_files = ['base.json', 'apps.json']

	def load(self):
		# Prepare + load directory.
		super().load()

		# Load the files and parse JSON.
		parsed_settings = dict()

		for file_name in self.files:
			try:
				file_path = os.path.join(self.directory, file_name)
				with open(file_path, 'r') as file_handle:
					parsed_settings.update(json.load(file_handle))
			except json.JSONDecodeError as e:
				raise ImproperlyConfigured(
					'Your settings file(s) contain invalid JSON syntax! Please fix and restart! File {}, Error {}'.format(
						file_name,
						str(e)
					)
				)

		# Loop and set in local settings (+ uppercase keys).
		for key, value in parsed_settings.items():
			self.settings[key.upper()] = value
