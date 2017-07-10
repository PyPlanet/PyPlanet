import os
import asynctest

from pyplanet.conf import settings


class TestConfiguration(asynctest.TestCase):

	async def tearDown(self):
		os.environ['PYPLANET_SETTINGS_METHOD'] = 'python'
		settings.reset()

	async def test_lazy_loading(self):
		settings.reset()
		assert settings.configured is False
		_ = settings.DEBUG
		assert settings.configured is True
		assert type(settings.DEBUG) is bool

	async def test_python_backend(self):
		settings.reset()
		os.environ['PYPLANET_SETTINGS_METHOD'] = 'python'

		assert settings.SETTINGS_METHOD == 'python'
		assert type(settings.DEBUG) is bool
		assert settings.configured is True

	async def test_json_backend(self):
		settings.reset()
		os.environ['PYPLANET_SETTINGS_METHOD'] = 'json'

		assert settings.SETTINGS_METHOD == 'json'
		assert type(settings.DEBUG) is bool
		assert settings.configured is True

	async def test_yaml_backend(self):
		settings.reset()
		os.environ['PYPLANET_SETTINGS_METHOD'] = 'yaml'

		assert settings.SETTINGS_METHOD == 'yaml'
		assert type(settings.DEBUG) is bool
		assert settings.configured is True
