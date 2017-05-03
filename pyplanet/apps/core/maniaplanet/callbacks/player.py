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
	return dict(
		player=player, text=text, cmd=cmd
	)


async def handle_player_info_changed(source, signal, **kwargs):
	is_spectator =     		source['SpectatorStatus']			% 10
	is_temp_spectator =		(source['SpectatorStatus'] / 10)	% 10
	is_pure_spectator =		(source['SpectatorStatus'] / 100)	% 10
	auto_target =			(source['SpectatorStatus'] / 1000)	% 10
	target_id =				(source['SpectatorStatus'] / 10000)
	try:
		player = await Controller.instance.player_manager.get_player(login=source['Login'])
	except:
		player = None
	return dict(
		is_spectator=is_spectator, is_temp_spectator=is_temp_spectator, is_pure_spectator=is_pure_spectator,
		auto_target=auto_target, target_id=target_id, flags=source['Flags'], spectator_status=source['SpectatorStatus'],
		team_id=source['TeamId'], player_id=source['PlayerId'], player=player, player_login=source['Login'],
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

player_info_changed = Callback(
	call='ManiaPlanet.PlayerInfoChanged',
	namespace='maniaplanet',
	code='player_info_changed',
	target=handle_player_info_changed,
)
