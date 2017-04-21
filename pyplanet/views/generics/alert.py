from pyplanet.core.ui.components.manialink import StaticManiaLink
from pyplanet.core.ui.template import load_template


class Alert(StaticManiaLink):
	SIZES = dict(
		sm={
			'top__pos': '0 17',
			'top__size': '126.5 8',
			'box__size': '120 25',
			'bottom__pos': '0 -12',
			'bottom__size': '120 2',
			'text__pos': '-47.5 6.25',
			'text__size': '100 4',
			'button_0__pos__left': -32,
			'button_0__pos__top': -4,
			'button_1__pos__left': 32,
			'button_1__pos__top': -4,
		},
		md={
			'top__pos': '0 30',
			'top__size': '156.5 8',
			'box__size': '150 50',
			'bottom__pos': '0 -24',
			'bottom__size': '150 2',
			'text__pos': '-67.5 6.25',
			'text__size': '135 24',
			'button_0__pos__left': -32,
			'button_0__pos__top': -14,
			'button_1__pos__left': 32,
			'button_1__pos__top': -14,
		},
		lg={
			'top__pos': '0 55',
			'top__size': '206.5 8',
			'box__size': '200 100',
			'bottom__pos': '0 -50',
			'bottom__size': '200 2',
			'text__pos': '-92.5 6.25',
			'text__size': '185 74',
			'button_0__pos__left': -52,
			'button_0__pos__top': -40,
			'button_1__pos__left': 52,
			'button_1__pos__top': -40,
		},
	)

	def __init__(
		self, message, title='', size='md', buttons=None, manager=None
	):
		from pyplanet.core import Controller

		super().__init__(Controller.instance.ui_manager)
		sizes = self.SIZES[size]

		if not buttons:
			buttons = [{'name': 'OK'}]

		self.data = dict(
			title=title,
			message=message,
			buttons=buttons,
			sizes=sizes,
		)
		self.hide_click = True

	async def close(self, player, **kwargs):
		print('close')

	async def get_template(self):
		return await load_template('pyplanet.views', 'generics/alert.xml')
