from peewee import *
from pyplanet.core.db import Model


class AdvancedMap(Model):
	id = IntegerField()
	uid = CharField(max_length=50)
	name = CharField(max_length=150)
	author = CharField(max_length=100)
	karma = FloatField(null=True)
	local_record = IntegerField(null=True)
	local_record_count = IntegerField(null=True)
	player_local = IntegerField(null=True)
	player_local_rank = IntegerField(null=True)
