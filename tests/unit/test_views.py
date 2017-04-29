import asynctest

from pyplanet.core import Controller
from pyplanet.views.generics import AlertView
from pyplanet.views.generics.alert import PromptView


class TestGenericViews(asynctest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.instance = Controller.prepare(name='default').instance

	async def setUp(self):
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
