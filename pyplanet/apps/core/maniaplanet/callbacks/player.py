import datetime
from peewee import DoesNotExist

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.events import Callback
from pyplanet.core.instance import Controller


async def handle_player_connect(source, signal, **kwargs):
	instance = Controller.instance
	login = str(source[0])
	info = await instance.gbx.execute('GetDetailedPlayerInfo', login)
	ip, _, port = info['IPAddress'].rpartition(':')
	try:
		player = Player.get(login=login)
		player.last_ip = ip
		player.last_seen = datetime.datetime.now()
		player.save()
	except DoesNotExist:
		# Get details of player from dedicated.
		player = Player.create(
			login=login,
			nickname=info['NickName'],
			last_ip=ip,
			last_seen=datetime.datetime.now()
		)

	return dict(
		player=player, source=source, signal=signal,
	)


async def handle_player_chat(source, signal, **kwargs):
	player_uid, player_login, text, cmd = source
	# TODO: Get player.
	# TODO: Command abstraction.
	return dict(
		player=player_login, text=text, cmd=cmd
	)


Callback(
	call='ManiaPlanet.PlayerConnect',
	namespace='maniaplanet',
	code='player_connect',
	target=handle_player_connect,
)

Callback(
	call='ManiaPlanet.PlayerChat',
	namespace='maniaplanet',
	code='player_chat',
	target=handle_player_chat,
)
