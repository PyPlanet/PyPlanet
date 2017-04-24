from peewee import *

from pyplanet.apps.core.pyplanet.models import Permission
from pyplanet.core.db import Model


class SettingCategory(Model):
	code = CharField(
		max_length=100,
		null=False,
		unique=True,
		index=True
	)

	name = CharField(
		max_length=255,
		null=False
	)


class Setting(Model):
	app = CharField(
		max_length=255,
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
