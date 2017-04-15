from pyplanet.core.ui.components.manialink import StaticManiaLink
from pyplanet.core.ui.template import load_template


class Alert(StaticManiaLink):
	SIZES = dict(
		sm={
			'box_width': 100,
			'box_height': 50,
			'bar_left': -50,
			'bar_top': 15,
		},
		md={
			'box_width': 150,
			'box_height': 75,
			'bar_left': -75,
			'bar_top': 27,
		},
		lg={
			'box_width': 200,
			'box_height': 100,
			'bar_left': -100,
			'bar_top': 40,
		},
	)

	def __init__(
		self, title, message, size='md', button_text='OK', icon_style='Icons128x128_1', icon_substyle='Editor', manager=None
	):
		from pyplanet.core import Controller

		super().__init__(Controller.instance.ui_manager)
		sizes = dict()
		sizes.update(self.SIZES[size])

		# Calculate other sizes
		sizes['icon_top'] = (sizes['box_height'] / 2) - 1
		sizes['icon_left'] = -((sizes['box_width'] / 2) - 3)
		sizes['title_top'] = (sizes['box_height'] / 2) - 3
		sizes['message_left'] = -((sizes['box_width'] / 2) - 9)
		sizes['message_top'] = ((sizes['box_height']) / 2 - 17)
		sizes['message_width'] = sizes['box_width'] - 18
		sizes['message_height'] = sizes['box_height'] - 30
		sizes['buttons_top'] = -((sizes['box_height'] / 2) - 12)
		sizes['buttons_labels_top'] = sizes['buttons_top'] - 2

		self.data = dict(
			title=title,
			message=message,
			icon_style=icon_style,
			icon_substyle=icon_substyle,
			button_text=button_text,
			sizes=sizes,
			action='core__generics__alert_ok',
		)
		self.hide_click = True

	async def get_template(self):
		return await load_template('pyplanet.views', 'generics/alert.xml')
