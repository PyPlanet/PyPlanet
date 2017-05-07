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
	try:
		target = await Controller.instance.player_manager.get_player_by_id(target_id)
	except:
		target = None
	return dict(
		is_spectator=is_spectator, is_temp_spectator=is_temp_spectator, is_pure_spectator=is_pure_spectator,
		auto_target=auto_target, target_id=target_id, target=target, flags=source['Flags'],
		spectator_status=source['SpectatorStatus'], team_id=source['TeamId'],
		player_id=source['PlayerId'], player=player, player_login=source['Login'],
	)


player_connect = Callback(
	call='ManiaPlanet.PlayerConnect',
	namespace='maniaplanet',
	code='player_connect',
	target=handle_player_connect,
)
"""
:Signal: 
	Player has been connected.
:Code:
	``maniaplanet:player_connect``
:Description:
	Callback sent when a player connects and we fetched our data.
:Original Callback:
	`Native` Maniaplanet.PlayerConnect

:param player: Player instance
:param is_spectator: Boolean determinating if the player joined as spectator.
:param source: Raw payload, best to not use!
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""

player_disconnect = Callback(
	call='ManiaPlanet.PlayerDisconnect',
	namespace='maniaplanet',
	code='player_disconnect',
	target=handle_player_disconnect,
)
"""
:Signal: 
	Player has been disconnected.
:Code:
	``maniaplanet:player_disconnect``
:Description:
	Callback sent when a player disconnects.
:Original Callback:
	`Native` Maniaplanet.PlayerDisconnect

:param player: Player instance
:param reason: Reason of leave
:param source: Raw payload, best to not use!
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""

player_chat = Callback(
	call='ManiaPlanet.PlayerChat',
	namespace='maniaplanet',
	code='player_chat',
	target=handle_player_chat,
)
"""
:Signal: 
	Player has been writing a chat entry. When the server writes something we **wont** inform it in here!
:Code:
	``maniaplanet:player_chat``
:Description:
	Callback sent when a player chats.
:Original Callback:
	`Native` Maniaplanet.PlayerChat

:param player: Player instance
:param text: Text of chat
:param cmd: Boolean if it's a command. Be aware, you should use the ``command`` manager for commands!
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


player_info_changed = Callback(
	call='ManiaPlanet.PlayerInfoChanged',
	namespace='maniaplanet',
	code='player_info_changed',
	target=handle_player_info_changed,
)
"""
:Signal: 
	Player has changed status.
:Code:
	``maniaplanet:player_info_changed``
:Description:
	Callback sent when a player changes from state or information.
:Original Callback:
	`Native` Maniaplanet.PlayerInfoChanged

:param player: Player instance (COULD BE NONE SOMETIMES!).
:param player_login: Player login string.
:param is_spectator: Is player spectator (bool).
:param is_temp_spectator: Is player temporary spectator (bool).
:param is_pure_spectator: Is player pure spectator (bool).
:param auto_target: Player using auto target.
:param target_id: The target player id (not login!).
:param target: The target player instance or None if not found/none spectating.
:param flags: Raw flags.
:param spectator_status: Raw spectator status.
:param team_id: Team ID of player.
:param player_id: Player ID (server id).
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type target: pyplanet.apps.core.maniaplanet.models.player.Player
"""
