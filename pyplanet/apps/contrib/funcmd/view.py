"""
Toolbar View.
"""
from pyplanet.views import TemplateView


class EmojiToolbarView(TemplateView):
	template_name = 'funcmd/emoji_toolbar.xml'

	def __init__(self, app):
		"""
		Initiate the toolbar view.

		:param app: Player app instance.
		:type app: pyplanet.apps.contrib.funcmd.FunCmd
		"""
		super().__init__(app.context.ui)

		self.app = app
		self.instance = app.instance
		self.id = 'funcmd_emoji_toolbar'
		self.emoji_list = [
			'',  # Smiley
			'',  # Neutral Smiley
			'',  # Unhappy Smiley
			'$F30$z',  # Thumbs-down
			'$393$z',  # Thumbs-up
			'',  # Two fingers left
			'',  # Two fingers right
			'$F30$z',  # Heart <3
			'',  # Map/locator
			'$cc0🏆$z',  # Cup
		]

		for i in range(1, 11):
			self.subscribe('bar_button_{}'.format(i), self.action_emoji(self.emoji_list[i-1]))

	async def get_context_data(self):
		data = await super().get_context_data()
		data['game'] = self.app.instance.game.game
		return data

	def action_emoji(self, emoji):
		async def send_emoji(player, *args, **kwargs):
			if 'admin' in self.instance.apps.apps and self.instance.apps.apps['admin'].server.chat_redirection:
				return
			await self.instance.chat(
				'$z[{}$z] $z{}'.format(player.nickname, emoji)
			)
		return send_emoji
