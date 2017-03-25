from pyplanet.core.events import Callback
from pyplanet.core.exceptions import SignalGlueStop
from pyplanet.core.instance import Controller


async def handle_player_connect(source, signal, **kwargs):
	player_login, is_spectator = source
	player = await Controller.instance.player_manager.handle_connect(login=player_login)
	return dict(
		player=player, is_spectator=is_spectator, source=source, signal=signal,
	)


async def handle_player_disconnect(source, signal, **kwargs):
	player_login, reason = source
	player = await Controller.instance.player_manager.handle_disconnect(login=player_login)
	return dict(
		player=player, reason=reason, source=source, signal=signal,
	)


async def handle_player_chat(source, signal, **kwargs):
	player_uid, player_login, text, cmd = source
	if Controller.instance.game.server_player_login == player_login and Controller.instance.game.server_is_dedicated:
		raise SignalGlueStop('We won\'t inform anything about the chat we send ourself!')
	player = await Controller.instance.player_manager.get_player(login=player_login)
	# TODO: Command abstraction.
	return dict(
		player=player, text=text, cmd=cmd
	)


player_connect = Callback(
	call='ManiaPlanet.PlayerConnect',
	namespace='maniaplanet',
	code='player_connect',
	target=handle_player_connect,
)

player_disconnect = Callback(
	call='ManiaPlanet.PlayerDisconnect',
	namespace='maniaplanet',
	code='player_disconnect',
	target=handle_player_disconnect,
)

player_chat = Callback(
	call='ManiaPlanet.PlayerChat',
	namespace='maniaplanet',
	code='player_chat',
	target=handle_player_chat,
)
