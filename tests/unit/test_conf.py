import asynctest

from pyplanet.conf import settings


class TestConfiguration(asynctest.TestCase):
	async def test_lazy_loading(self):
		settings.reset()
		assert settings.configured is False
		_ = settings.DEBUG
		assert settings.configured is True
		assert type(settings.DEBUG) is bool
