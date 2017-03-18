from pyplanet.core.events import Callback


def handle_player_connect(data):
	return data


def handle_player_chat(data):
	return data


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
