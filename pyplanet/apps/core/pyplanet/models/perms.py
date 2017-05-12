from peewee import *

from pyplanet.core.db import Model


class Permission(Model):
	namespace = CharField(
		max_length=150,
		null=False,
		help_text='Namespace of the permission. Mostly the app.label.'
	)

	name = CharField(
		max_length=150,
		null=False,
		help_text='Name of permission, in format {app_name|core}:{name}'
	)

	description = TextField(
		null=True, default=None, help_text='Description of permission.'
	)

	min_level = IntegerField(
		default=1, help_text='Minimum required player level to be able to use this permission.'
	)

	class Meta:
		indexes = (
			(('namespace', 'name'), True),
		)
