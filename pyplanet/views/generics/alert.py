from pyplanet.views import TemplateView


class AlertView(TemplateView):
	"""
	The AlertView can be used to show several generic alerts to a player. You can use 3 different sizes, and adjust the
	message text.
	
	The 3 sizes:
	sm, md and lg.
	"""

	template_package = 'pyplanet.views'
	template_name = 'generics/alert.xml'

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
		"""
		Create an AlertView instance.
		
		:param message: The message to display to the end-user, Use ``\\n`` for new lines. You can use symbols from FontAwesome
						by using Unicode escaped strings.
		:param title: Title of message, currently not implemented for any size!
		:param size: Size to use, this parameter should be a string, and one of the following choices:
					 'sm', 'md' or 'lg. Defaults to 'md'.
		:param buttons: Buttons to display, Should be an array with dictionary which contain: name.
		:param manager: UI Manager to use, You should always keep this undefined unless you know what your doing!
		
		:type message: str
		:type title: str
		:type size: str
		:type buttons: list
		:type manager: pyplanet.core.ui._BaseUIManager
		"""
		from pyplanet.core import Controller

		super().__init__(manager or Controller.instance.ui_manager)
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
		"""
		Close the alert.
		"""
		await self.hide(player_logins=[player.login])
