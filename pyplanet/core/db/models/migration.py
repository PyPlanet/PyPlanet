from peewee import *
from .. import Proxy


class Migration(Model):
	app = CharField()
	name = CharField()
	applied = BooleanField()

	class Meta:
		database = Proxy
