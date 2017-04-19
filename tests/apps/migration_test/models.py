from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.db import TimedModel

from peewee import *


class TestModel(TimedModel):
	player = ForeignKeyField(Player)
	test = BooleanField(default=True)
	sample_field = CharField(default='unknown', db_column='sample')
