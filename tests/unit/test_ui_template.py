import asynctest
from jinja2 import Template

from pyplanet.core import Controller
from pyplanet.core.ui.template import load_template


class TestTemplate(asynctest.TestCase):
	async def test_template_loading(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()
		template = await load_template('core.views/generics/list.xml')
		assert template and template.template
		assert isinstance(template.template, Template)

	async def test_template_rendering(self):
		instance = Controller.prepare(name='default').instance
		await instance.db.connect()
		await instance.apps.discover()
		template = await load_template('core.views/generics/list.xml')
		body = await template.render(
			title='TRY_TO_SEARCH_THIS'
		)
		assert 'TRY_TO_SEARCH_THIS' in body
