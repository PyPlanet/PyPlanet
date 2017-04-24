from peewee import DoesNotExist

from pyplanet.apps.core.pyplanet.models.setting import Setting as SettingModel


class Setting:
	def __init__(
		self, key: str, name: str, type=str, description: str = None, category: str = None, default=None,
	):
		"""
		Create setting with properties.
		
		:param key: Key of setting, this is mainly only used for the backend and for referencing the setting. You should
		keep this unique in your app!
		:param name: Name of the setting that will be displayed as a small label to the player.
		:param type: Type of value to expect, use python types here. str by default.
		:param description: Description to provide help and instructions to the player.
		:param category: Category in string, must exactly match other category names. None for no category (default).
		:param default: Default value if not provided from database. This will be returned. Defaults to None.
		"""
		# Prepare property for app specific setting. Will be injected by the register command.
		self.app_label = None

		self.key = key
		self.name = name
		self.description = description
		self.category = category
		self.default = default
		self.type = type

		# Prepare the model instance here. This will be filled once it's fetched for the first time (or inited).
		self._instance = None
		self._value = None

	async def initiate_setting(self):
		"""
		Initiate database record for setting.
		"""
		return await SettingModel.get_or_create_from_info(
			key=self.key, app=self.app_label, category=self.category, name=self.name, description=self.description,
			value=None
		)
