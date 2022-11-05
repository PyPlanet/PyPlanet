"""
Maniaplanet Core Models. This models are used in several apps and should be considered as very stable.
"""
from peewee import *
from pyplanet.core.db import TimedModel
from pyplanet.apps.core.maniaplanet.models import Player, Map


class MapFolder(TimedModel):
	player = ForeignKeyField(Player, index=True)
	"""
	The player who created the folder.
	"""

	name = CharField(
		max_length=50,
		null=False,
	)
	"""
	Folder name
	"""

	visibility = CharField(
		max_length=50,
		null=False,
		default='private'
	)
	"""
	Visibility of the folder (public, private, admin_only).
	"""

	@property
	def icon(self):
		if self.visibility == 'public':
			return '\uf0c0'
		elif self.visibility == 'admins_only':
			return '\uf0c1'
		return '\uf023'


class MapInFolder(TimedModel):
	map = ForeignKeyField(Map, index=True)
	"""
	Map belonging to a folder.
	"""

	folder = ForeignKeyField(MapFolder, index=True)
	"""
	Folder the map belongs to.
	"""

