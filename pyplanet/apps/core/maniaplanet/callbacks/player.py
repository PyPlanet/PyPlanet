from pyplanet.core.events import Callback


async def handle_player_connect(**data):
	print(data)
	return data


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
