import asyncio
import re

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.views import TemplateView


class AlertView(TemplateView):
	"""
	The AlertView can be used to show several generic alerts to a player. You can use 3 different sizes, and adjust the
	message text.

	The 3 sizes:
	sm, md and lg.
	"""

	template_name = 'core.views/generics/alert.xml'

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
		self, message, size='md', buttons=None, manager=None, target=None, **data
	):
		"""
		Create an AlertView instance.

		:param message: The message to display to the end-user, Use ``\\n`` for new lines. You can use symbols from FontAwesome
						by using Unicode escaped strings.
		:param size: Size to use, this parameter should be a string, and one of the following choices:
					 'sm', 'md' or 'lg. Defaults to 'md'.
		:param buttons: Buttons to display, Should be an array with dictionary which contain: name.
		:param manager: UI Manager to use, You should always keep this undefined unless you know what your doing!
		:param target: Target coroutine method called as handle of button clicks.

		:type message: str
		:type title: str
		:type size: str
		:type buttons: list
		:type manager: pyplanet.core.ui._BaseUIManager
		"""
		from pyplanet.core import Controller

		super().__init__(manager or Controller.instance.ui_manager)
		self.disable_alt_menu = True
		sizes = self.SIZES[size]

		if not buttons:
			buttons = [{'name': 'OK'}]

		self.target = target
		self.response_future = asyncio.Future()

		self.data = dict(
			message=message,
			buttons=buttons,
			sizes=sizes,
		)
		self.data.update(data)

	async def wait_for_reaction(self):  # pragma: no cover
		"""
		Wait for reaction or input and return it.

		:return: Returns the button clicked or the input value string of the user.
		"""
		return await self.response_future

	async def handle(self, player, action, values, **kwargs):  # pragma: no cover
		await self.close(player)

		# Try to parse the button id instead of the whole action string.
		button = action
		try:
			match = re.search('button_([0-9]+)$', action)
			if len(match.groups()) == 1:
				button = match.group(1)
		except:
			pass

		if not self.response_future.done():
			self.response_future.set_result(button)

		if self.target:
			await self.target(player, action, values, **kwargs)

	async def close(self, player, **kwargs):  # pragma: no cover
		"""
		Close the alert.
		"""
		await self.hide(player_logins=[player.login])


class PromptView(AlertView):
	"""
	The PromptView is like the AlertView but can ask for a text entry.

	The 3 sizes:
	sm, md and lg.

	You can listen for the results of the players input with the ``wait_for_input()`` async handler (future).
	Example:

	.. code-block:: python

		prompt = PromptView('Please enter your name')
		await prompt.display(['login'])

		user_input = await prompt.wait_for_input()
		print(user_input)


	You can do validations before it's okay with giving a function to the argument ``validator``. Example:

	.. code-block:: python

		def my_validator(value):
			try:
				int(value)
				return True, None
			except:
				return False, 'Value should be an integer!'

		prompt = PromptView('Please enter your name', validator=my_validator)
		await prompt.display(['login'])

		user_input = await prompt.wait_for_input()
		print(user_input)

	"""

	template_name = 'core.views/generics/prompt.xml'

	SIZES = dict(
		sm={
			'top__pos': '0 24',
			'top__size': '126.5 8',
			'box__size': '120 40',
			'bottom__pos': '0 -20',
			'bottom__size': '120 2',
			'text__pos': '-47.5 11',
			'text__size': '100 4',
			'input__pos': '0 0',
			'input__size': '100 7',
			'button_0__pos__left': -32,
			'button_0__pos__top': -12,
			'button_1__pos__left': 32,
			'button_1__pos__top': -12,
		},
		md={
			'top__pos': '0 38',
			'top__size': '156.5 8',
			'box__size': '150 67',
			'bottom__pos': '0 -34',
			'bottom__size': '150 2',
			'text__pos': '-67.5 11',
			'text__size': '135 24',
			'input__pos': '0 -10',
			'input__size': '135 7',
			'button_0__pos__left': -32,
			'button_0__pos__top': -24,
			'button_1__pos__left': 32,
			'button_1__pos__top': -24,
		},
		lg={
			'top__pos': '0 67',
			'top__size': '206.5 8',
			'box__size': '200 125',
			'bottom__pos': '0 -62',
			'bottom__size': '200 2',
			'text__pos': '-92.5 11',
			'text__size': '185 74',
			'input__pos': '0 -40',
			'input__size': '185 7',
			'button_0__pos__left': -52,
			'button_0__pos__top': -52,
			'button_1__pos__left': 52,
			'button_1__pos__top': -52,
		},
	)

	def __init__(self, message, size='md', buttons=None, manager=None, default='', validator=None):
		super().__init__(message, size, buttons, manager)
		self.disable_alt_menu = True

		self.default = default
		self.validator = validator or self.validate_input

	async def wait_for_input(self):  # pragma: no cover
		"""
		Wait for input and return it.

		:return: Returns the string value of the user.
		"""
		return await self.response_future

	def validate_input(self, value):  # pragma: no cover
		if not value or len(value) == 0:
			return False, 'Empty value given!'
		return True, None

	async def handle(self, player, action, values, **kwargs):  # pragma: no cover
		self.data['errors'] = ''
		value = self.default
		if 'prompt_value' in values:
			value = values['prompt_value']

		valid, message = self.validator(value)

		if valid:
			await self.close(player)
			if not self.response_future.done():
				self.response_future.set_result(value)
			return

		self.data['errors'] = message
		await self.display([player.login])

# Util methods.
async def ask_confirmation(player, message, size='md', buttons=None):  # pragma: no cover
	"""
	Ask the player for confirmation and return the button number (0 is first button).

	:param player: Player login or instance.
	:param message: Message to display.
	:param size: Size, could be 'sm', 'md', or 'lg'.
	:param buttons: Buttons, optional, default is yes and no.
	:return: Number of button that is clicked.
	"""
	buttons = buttons or [{'name': 'Yes'}, {'name': 'No'}]
	view = AlertView(message, size, buttons)
	if isinstance(player, Player):
		player = player.login
	await view.display(player_logins=[player])
	reaction = await view.wait_for_reaction()
	try:
		reaction = int(reaction)
	except:
		reaction = None
	del view
	return reaction
