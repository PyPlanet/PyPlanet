import os
import yaml

from pyplanet.conf.backends.file import FileConfigBackend
from pyplanet.core.exceptions import ImproperlyConfigured


class YamlConfigBackend(FileConfigBackend):
	name = 'yaml'
	files = ['base.yaml', 'apps.yaml']
	required_files = ['base.yaml', 'apps.yaml']

	def load(self):
		# Prepare + load directory.
		super().load()

		# Load the files and parse Yaml.
		parsed_settings = dict()

		try:
			for file_name in self.files:
				file_path = os.path.join(self.directory, file_name)
				with open(file_path, 'r') as file_handle:
					parsed_settings.update(yaml.safe_load(file_handle))
		except (yaml.YAMLError, yaml.MarkedYAMLError) as e:
			raise ImproperlyConfigured(
				'Your settings file(s) contain invalid YAML syntax! Please fix and restart!, {}'.format(str(e))
			)

		# Loop and set in local settings (+ uppercase keys).
		for key, value in parsed_settings.items():
			self.settings[key.upper()] = value
