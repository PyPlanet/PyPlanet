"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
from peewee import *
from pyplanet.core.db import TimedModel


class Player(TimedModel):
	login = CharField(
		max_length=100,
		null=False,
		index=True,
		unique=True
	)
	"""
	The login of the player will be the unique index we use in the player table.
	"""

	nickname = CharField(max_length=150)
	"""
	The nickname of the player including maniaplanet styles.
	"""

	last_ip = CharField(max_length=46)
	"""
	The last used IP-address for the player.
	"""

	last_seen = DateTimeField(null=True, default=None)
	"""
	When is the player last seen on the server.
	"""
