from jinja2 import Template

from pyplanet.core.ui.template import load_template

from tests.base import TestCase


class TestTemplate(TestCase):
	async def test_template_loading(self):
		instance = self.instance
		await instance.db.connect()
		await instance.apps.discover()
		template = await load_template('core.views/generics/list.xml')
		assert template and template.template
		assert isinstance(template.template, Template)

	async def test_template_rendering(self):
		instance = self.instance
		await instance.db.connect()
		await instance.apps.discover()
		template = await load_template('core.views/generics/list.xml')
		body = await template.render(
			title='TRY_TO_SEARCH_THIS'
		)
		assert 'TRY_TO_SEARCH_THIS' in body
