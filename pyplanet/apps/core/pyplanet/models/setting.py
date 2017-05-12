from peewee import *

from pyplanet.core.db import Model


class Setting(Model):
	"""
	DON'T USE THIS DIRECTLY, USE THE CONTRIB MANAGER!
	"""

	app = CharField(
		max_length=150,
		null=True,
		index=True,
		default=None,
	)
	"""
	App label of setting. None for core (never use None for this outside of the manager itself!!).
	"""

	key = CharField(
		max_length=150,
		null=False,
		index=True
	)
	"""
	The key of the setting, together with app unique!
	"""

	category = CharField(
		max_length=100,
		null=True,
		default=None
	)
	"""
	Name of category, all items will be under a special label or menu item.
	"""

	name = CharField(
		max_length=255,
		null=False,
		help_text='Name of setting.'
	)
	"""
	Name of the setting. Will be displayed in a list.
	"""

	description = TextField(
		null=True,
		default=None,
		help_text='Description of the setting.'
	)
	"""
	Description of the setting contains the information to help the user with filling in the field(s).
	"""

	value = TextField(
		null=True,
		default=None,
	)
	"""
	The value, fitted in a text field so we can parse it quite easy.
	"""

	class Meta:
		indexes = (
			(('app', 'key'), True),
		)

	def __str__(self):
		return '{} ({}:{})'.format(self.app, self.key, self.name)

	@classmethod
	async def get_or_create_from_info(cls, key, app, **kwargs):
		"""
		This method will be called from the core, getting or creating a setting instance from the information we got from
		the setting instance (static setting object).
		
		:param key: Key of setting.
		:param app: App label.
		:param kwargs: Other key arguments, matching the model columns!
		:return: Setting instance.
		"""
		needs_save = False
		try:
			setting = await cls.get(key=key, app=app)
		except DoesNotExist:
			setting = cls(key=key, app=app)
			needs_save = True

		# Update from the kwargs.
		for k, v in kwargs.items():
			if v is not None and hasattr(setting, k) and getattr(setting, k) != v:
				setattr(setting, k, v)
				needs_save = True

		if needs_save:
			await setting.save()

		return setting
