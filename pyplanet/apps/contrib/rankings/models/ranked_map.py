from peewee import *
from pyplanet.core.db import Model


class RankedMap(Model):
	id = IntegerField()
	name = CharField(max_length=150)
	uid = CharField(max_length=50)
	author_login = CharField(max_length=100)
	player_rank = IntegerField()
