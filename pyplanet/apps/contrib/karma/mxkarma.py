from pyplanet.contrib.setting import Setting

from pyplanet.apps.contrib.karma.mxkarmaapi import MXKarmaApi


class MXKarma:
	def __init__(self, app):
		self.app = app
		self.api = MXKarmaApi(self)

		self.setting_mx_karma = Setting(
			'mx_karma', 'Enable MX Karma', Setting.CAT_BEHAVIOUR, type=bool,
			description='Enabling MX Karma will provide you with global karma information from ManiaExchange.',
			default=False, change_target=self.reload_settings
		)

		self.setting_mx_karma_key = Setting(
			'mx_karma_key', 'MX Karma API Key', Setting.CAT_BEHAVIOUR, type=str,
			description='Enabling MX Karma will provide you with global karma information from ManiaExchange.',
			default=None, change_target=self.reload_settings
		)

	async def reload_settings(self, *args, **kwargs):
		enabled = await self.setting_mx_karma.get_value()
		key = await self.setting_mx_karma_key.get_value()

		if enabled is True and key is not None:
			await self.api.create_session()
			await self.api.start_session()
		else:
			await self.api.close_session()

	async def handle_rating(self, rating):
		pass

	async def on_start(self):
		await self.app.context.setting.register(
			self.setting_mx_karma, self.setting_mx_karma_key
		)

		if await self.setting_mx_karma.get_value() is False or await self.setting_mx_karma_key.get_value() is None:
			return

		await self.api.create_session()
		await self.api.start_session()

		rating = await self.api.get_map_rating(self.app.instance.map_manager.current_map)
		if rating is not None:
			await self.handle_rating(rating)

	async def on_stop(self):
		if await self.setting_mx_karma.get_value() is False or await self.setting_mx_karma_key.get_value() is None:
			return

		await self.api.close_session()

	async def player_connect(self, player):
		rating = await self.api.get_map_rating(self.app.instance.map_manager.current_map, player.login)

	async def map_begin(self, map):
		if await self.setting_mx_karma.get_value() is False or await self.setting_mx_karma_key.get_value() is None:
			return

		if not self.api.activated:
			return

		rating = await self.api.get_map_rating(self.app.instance.map_manager.current_map)
		if rating is not None:
			await self.handle_rating(rating)

	async def map_end(self, map):
		if await self.setting_mx_karma.get_value() is False or await self.setting_mx_karma_key.get_value() is None:
			return

		if not self.api.activated:
			return
