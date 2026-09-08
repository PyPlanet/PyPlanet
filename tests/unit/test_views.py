from pyplanet.views.generics import AlertView
from pyplanet.views.generics.alert import PromptView

from tests.base import TestCase


class TestGenericViews(TestCase):
	async def setUp(self):
		await super().setUp()
		await self.instance.apps.discover()

	async def test_alert(self):
		view = AlertView(message='TestMessage', size='sm')
		body = await view.render()
		assert 'TestMessage' in body

		view = AlertView(message='TestMessage', size='md')
		body = await view.render()
		assert 'TestMessage' in body

		view = AlertView(message='TestMessage', size='lg')
		body = await view.render()
		assert 'TestMessage' in body

	async def test_prompt(self):
		view = PromptView(message='TestMessage', size='sm')
		body = await view.render()
		assert 'TestMessage' in body

		view = PromptView(message='TestMessage', size='md')
		body = await view.render()
		assert 'TestMessage' in body

		view = PromptView(message='TestMessage', size='lg')
		body = await view.render()
		assert 'TestMessage' in body
