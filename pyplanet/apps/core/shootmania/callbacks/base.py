"""
:Weapons:
	[1-Laser, 2-Rocket, 3-Nucleus, 5-Arrow]
"""
import asyncio

from pyplanet.core import Controller
from pyplanet.core.events import Callback, handle_generic


async def _get_player(login):
	try:
		if not login or not len(login):
			return None
		return await Controller.instance.player_manager.get_player(login=login)
	except:
		return None


async def handle_on_shoot(source, signal, **kwargs):
	shooter = await Controller.instance.player_manager.get_player(login=source['shooter'])
	return dict(shooter=shooter, time=source['time'], weapon=source['weapon'])

async def handle_on_hit(source, signal, **kwargs):
	victim, shooter = await asyncio.gather(*[
		_get_player(source['victim']),
		_get_player(source['shooter']),
	])
	return dict(
		shooter=shooter, time=source['time'], weapon=source['weapon'], victim=victim, damage=source['damage'],
		points=source['points'], distance=source['distance'],
		shooter_position=source['shooterposition'], victim_position=source['victimposition'],
	)

async def handle_on_near_miss(source, signal, **kwargs):
	victim, shooter = await asyncio.gather(*[
		_get_player(source['victim']),
		_get_player(source['shooter']),
	])
	return dict(
		shooter=shooter, time=source['time'], weapon=source['weapon'], victim=victim, distance=source['distance'],
		shooter_position=source['shooterposition'], victim_position=source['victimposition'],
	)

async def handle_armor_empty(source, signal, **kwargs):
	victim, shooter = await asyncio.gather(
		_get_player(source['victim']),
		_get_player(source['shooter']),
	)

	return dict(
		shooter=shooter, time=source['time'], weapon=source['weapon'], victim=victim, distance=source['distance'],
		shooter_position=source['shooterposition'], victim_position=source['victimposition'],
	)

async def handle_on_capture(source, signal, **kwargs):
	players = await asyncio.gather(*[
		Controller.instance.player_manager.get_player(login=p)
		for p in source['players']
	])
	return dict(time=source['time'], players=players, landmark=source['landmark'])

async def handle_on_shot_deny(source, signal, **kwargs):
	victim, shooter = await asyncio.gather(*[
		_get_player(source['victim']),
		_get_player(source['shooter']),
	])
	return dict(
		time=source['time'], shooter=shooter, victim=victim,
		shooter_weapon=source['shooterweapon'], victim_weapon=source['victimweapon']
	)

async def handle_on_fall_damage(source, signal, **kwargs):
	victim = await Controller.instance.player_manager.get_player(login=source['victim'])
	return dict(time=source['time'], victim=victim)

async def handle_player_added(source, signal, **kwargs):
	player = await Controller.instance.player_manager.get_player(login=source['login'])
	return dict(
		time=source['time'], player=player, team=source['team'], language=source['language'],
		ladder_rank=source['ladderrank'], ladder_points=source['ladderpoints']
	)

async def handle_custom_event(source, signal, **kwargs):
	victim, shooter = await asyncio.gather(*[
		_get_player(source['victim']),
		_get_player(source['shooter']),
	])
	source['shooter'] = shooter
	source['victim'] = victim
	return source

async def handle_action_event(source, signal, **kwargs):
	player = await _get_player(login=source['login'])
	return dict(time=source['time'], player=player, action_input=source['actioninput'])

async def handle_player_touches_object(source, signal, **kwargs):
	player = await _get_player(login=source['login'])
	return dict(
		time=source['time'], player=player, object_id=source['objectid'], model_id=source['modelid'], model_name=source['modelname']
	)

async def handle_player_triggers_sector(source, signal, **kwargs):
	player = await _get_player(login=source['login'])
	return dict(time=source['time'], player=player, sector_id=source['sectorid'])

async def handle_player_request_action_change(source, signal, **kwargs):
	player = await _get_player(login=source['login'])
	return dict(time=source['time'], player=player, action_change=source['actionchange'])

async def handle_scores(source, signal, **kwargs):
	async def get_player_scores(data):
		player = await _get_player(login=data['login'])
		return dict(
			player=player, rank=data['rank'], round_points=data['roundpoints'], map_points=data['mappoints'],
			match_points=data['matchpoints'],
		)
	async def get_team_scores(data):
		return dict(
			name=data['name'], id=data['id'], round_points=data['roundpoints'],
			map_points=data['mappoints'], match_points=data['matchpoints'],
		)

	player_scores = await asyncio.gather(*[
		get_player_scores(d) for d in source['players']
	])
	team_scores = await asyncio.gather(*[
		get_team_scores(d) for d in source['teams']
	])
	return dict(
		players=player_scores,
		teams=team_scores,
		winner_team=source['winnerteam'],
		use_teams=source['useteams'],
		winner_player=source['winnerplayer'],
		section=source['section']
	)

#######################################################################################
# Generic
#######################################################################################

on_shoot = Callback(
	call='Script.Shootmania.Event.OnShoot',
	namespace='shootmania',
	code='on_shoot',
	target=handle_on_shoot,
)
"""
:Signal: 
	Player shoot.
:Code:
	``shootmania:on_shoot``
:Description:
	Callback sent when a player shoots.
:Original Callback:
	`Script` Shootmania.Event.OnShoot

:param shooter: Shooter, Player instance
:param time: Time of server when callback is sent.
:param weapon: Weapon number.
:type shooter: pyplanet.apps.core.maniaplanet.models.player.Player
"""

on_hit = Callback(
	call='Script.Shootmania.Event.OnHit',
	namespace='shootmania',
	code='on_hit',
	target=handle_on_hit,
)
"""
:Signal: 
	Player hit.
:Code:
	``shootmania:on_hit``
:Description:
	Callback sent when a player is hit.
:Original Callback:
	`Script` Shootmania.Event.OnHit

:param shooter: shooter, Player instance
:param time: Time of server when callback is sent.
:param weapon: Weapon number.
:param victim: victim, Player instance
:param damage: Damage done.
:param points: Points scored by hit.
:param distance: Distance between victim and shooter.
:param shooter_position: Position of shooter.
:param victim_position: Position of victim.
:type shooter: pyplanet.apps.core.maniaplanet.models.player.Player
:type victim: pyplanet.apps.core.maniaplanet.models.player.Player
"""

on_near_miss = Callback(
	call='Script.Shootmania.Event.OnNearMiss',
	namespace='shootmania',
	code='on_near_miss',
	target=handle_on_near_miss,
)
"""
:Signal: 
	Near Miss.
:Code:
	``shootmania:on_near_miss``
:Description:
	Callback sent when a player dodges a projectile.
:Original Callback:
	`Script` Shootmania.Event.OnNearMiss

:param shooter: shooter, Player instance
:param time: Time of server when callback is sent.
:param weapon: Weapon number.
:param victim: victim, Player instance
:param distance: Distance between victim and shooter.
:param shooter_position: Position of shooter.
:param victim_position: Position of victim.
:type shooter: pyplanet.apps.core.maniaplanet.models.player.Player
:type victim: pyplanet.apps.core.maniaplanet.models.player.Player
"""

on_armor_empty = Callback(
	call='Script.Shootmania.Event.OnArmorEmpty',
	namespace='shootmania',
	code='on_armor_empty',
	target=handle_armor_empty,
)
"""
:Signal: 
	Armor empty, player eliminated.
:Code:
	``shootmania:on_armor_empty``
:Description:
	Callback sent when a player is eliminated.
:Original Callback:
	`Script` Shootmania.Event.OnArmorEmpty

:param shooter: shooter, Player instance
:param time: Time of server when callback is sent.
:param weapon: Weapon number.
:param victim: victim, Player instance
:param distance: Distance between victim and shooter.
:param shooter_position: Position of shooter.
:param victim_position: Position of victim.
:type shooter: pyplanet.apps.core.maniaplanet.models.player.Player
:type victim: pyplanet.apps.core.maniaplanet.models.player.Player
"""


on_capture = Callback(
	call='Script.Shootmania.Event.OnCapture',
	namespace='shootmania',
	code='on_capture',
	target=handle_on_capture,
)
"""
:Signal: 
	Landmark has been captured
:Code:
	``shootmania:on_capture``
:Description:
	Callback sent when a landmark is captured.
:Original Callback:
	`Script` Shootmania.Event.OnCapture

time=source['time'], players=players, landmark=source['landmark']

:param time: Time of server when callback is sent.
:param players: Player list (instances).
:param landmark: Landmark information, raw!
:type players: pyplanet.apps.core.maniaplanet.models.player.Player[]
"""


on_shot_deny = Callback(
	call='Script.Shootmania.Event.OnShotDeny',
	namespace='shootmania',
	code='on_shot_deny',
	target=handle_on_shot_deny,
)
"""
:Signal: 
	Player denies a projectile.
:Code:
	``shootmania:on_shot_deny``
:Description:
	Callback sent when a player denies a projectile.
:Original Callback:
	`Script` Shootmania.Event.OnShotDeny

:param time: Time of server when callback is sent.
:param shooter: shooter, Player instance
:param victim: victim, Player instance
:param shooter_weapon: Weapon number of shooter.
:param victim_weapon: Weapon number of victim that denied the shot.
:param distance: Distance between victim and shooter.
:param shooter_position: Position of shooter.
:param victim_position: Position of victim.
:type shooter: pyplanet.apps.core.maniaplanet.models.player.Player
:type victim: pyplanet.apps.core.maniaplanet.models.player.Player
"""

on_fall_damage = Callback(
	call='Script.Shootmania.Event.OnFallDamage',
	namespace='shootmania',
	code='on_fall_damage',
	target=handle_on_fall_damage,
)
"""
:Signal: 
	Fall Damage
:Code:
	``shootmania:on_fall_damage``
:Description:
	Callback sent when a player suffers fall damage.
:Original Callback:
	`Script` Shootmania.Event.OnFallDamage

:param time: Time of server when callback is sent.
:param victim: victim, Player instance
:type victim: pyplanet.apps.core.maniaplanet.models.player.Player
"""


on_command = Callback(
	call='Script.Shootmania.Event.OnCommand',
	namespace='shootmania',
	code='on_command',
	target=handle_generic,
)
"""
:Signal: 
	On Command
:Code:
	``shootmania:on_command``
:Description:
	Callback sent when a command is executed on the server.
:Original Callback:
	`Script` Shootmania.Event.OnCommand

:param time: Time of server when callback is sent.
:param name: Name of the command
:param value: Value in dictionary of the command.
:type value: dict
"""


player_added = Callback(
	call='Script.Shootmania.Event.OnPlayerAdded',
	namespace='shootmania',
	code='player_added',
	target=handle_player_added,
)
"""
:Signal: 
	On player added.
:Code:
	``shootmania:player_added``
:Description:
	Callback sent when a player joins the server.
:Original Callback:
	`Script` Shootmania.Event.OnPlayerAdded

:param time: Time of server when callback is sent.
:param player: Player instance
:param team: Team nr.
:param language: Language code, like 'en'.
:param ladder_rank: Current ladder rank.
:param ladder_points: Current ladder points.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


player_removed = Callback(
	call='Script.Shootmania.Event.OnPlayerRemoved',
	namespace='shootmania',
	code='player_removed',
	target=handle_generic,
)
"""
:Signal: 
	On player removed.
:Code:
	``shootmania:player_removed``
:Description:
	Callback sent when a player leaves the server.
:Original Callback:
	`Script` Shootmania.Event.OnPlayerRemoved

:param time: Time of server when callback is sent.
:param login: Player login string
:param player: Player instance.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


player_request_respawn = Callback(
	call='Script.Shootmania.Event.OnPlayerRequestRespawn',
	namespace='shootmania',
	code='player_request_respawn',
	target=handle_generic,
)
"""
:Signal: 
	On player request respawn.
:Code:
	``shootmania:player_request_respawn``
:Description:
	Callback sent when a player presses the respawn button.
:Original Callback:
	`Script` Shootmania.Event.OnPlayerRequestRespawn

:param time: Time of server when callback is sent.
:param login: Player login string
:param player: Player instance.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


action_custom_event = Callback(
	call='Script.Shootmania.Event.OnActionCustomEvent',
	namespace='shootmania',
	code='action_custom_event',
	target=handle_custom_event,
)
"""
:Signal: 
	Handle Action Custom Event.
:Code:
	``shootmania:action_custom_event``
:Description:
	Callback sent when an action triggers a custom event.
:Original Callback:
	`Script` Shootmania.Event.OnActionCustomEvent

:param time: Time of server when callback is sent.
:param shooter: Shooter player instance if any
:param victim: Victim player instance if any
:param actionid: Action Identifier.
:param *: Any other params, like ``param1``, ``param2``, etc...
:type shooter: pyplanet.apps.core.maniaplanet.models.player.Player
:type victim: pyplanet.apps.core.maniaplanet.models.player.Player
"""


action_event = Callback(
	call='Script.Shootmania.Event.OnActionEvent',
	namespace='shootmania',
	code='action_event',
	target=handle_action_event,
)
"""
:Signal: 
	Handle Action Event.
:Code:
	``shootmania:action_event``
:Description:
	Callback sent when an action triggers an event.
:Original Callback:
	`Script` Shootmania.Event.OnActionEvent

:param time: Time of server when callback is sent.
:param login: Player login
:param player: Player instance.
:param action_input: Action input.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


player_touches_object = Callback(
	call='Script.Shootmania.Event.OnPlayerTouchesObject',
	namespace='shootmania',
	code='player_touches_object',
	target=handle_player_touches_object,
)
"""
:Signal: 
	Player Touches Object.
:Code:
	``shootmania:player_touches_object``
:Description:
	Callback sent when a player touches an object.
:Original Callback:
	`Script` Shootmania.Event.OnPlayerTouchesObject

:param time: Time of server when callback is sent.
:param player: Player instance.
:param object_id: Object Identifier.
:param model_id: Model identifier.
:param model_name: Model name.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


player_triggers_sector = Callback(
	call='Script.Shootmania.Event.OnPlayerTriggersSector',
	namespace='shootmania',
	code='player_triggers_sector',
	target=handle_player_triggers_sector,
)
"""
:Signal: 
	Player Triggers Sector.
:Code:
	``shootmania:player_triggers_sector``
:Description:
	Callback sent when a player triggers a sector.
:Original Callback:
	`Script` Shootmania.Event.OnPlayerTriggersSector

:param time: Time of server when callback is sent.
:param player: Player instance.
:param sector_id: Sector Identifier.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


player_throws_object = Callback(
	call='Script.Shootmania.Event.OnPlayerThrowsObject',
	namespace='shootmania',
	code='player_throws_object',
	target=handle_player_touches_object,  # Can be reused!
)
"""
:Signal: 
	Player Throws an object.
:Code:
	``shootmania:player_touch_object``
:Description:
	Callback sent when a player throws an object.
:Original Callback:
	`Script` Shootmania.Event.OnPlayerThrowsObject

:param time: Time of server when callback is sent.
:param player: Player instance.
:param object_id: Object Identifier.
:param model_id: Model identifier.
:param model_name: Model name.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


player_request_action_change = Callback(
	call='Script.Shootmania.Event.OnPlayerRequestActionChange',
	namespace='shootmania',
	code='player_request_action_change',
	target=handle_player_request_action_change,
)
"""
:Signal: 
	Player requests action change.
:Code:
	``shootmania:player_request_action_change``
:Description:
	Callback sent when a player requests to use another action.
:Original Callback:
	`Script` Shootmania.Event.OnPlayerRequestActionChange

:param time: Time of server when callback is sent.
:param player: Player instance.
:param action_change: Can be -1 (request previous action) or 1 (request next action)
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


scores = Callback(
	call='Script.Shootmania.Scores',
	namespace='shootmania',
	code='scores',
	target=handle_scores
)
"""
:Signal: 
	Score callback, called after the map. (Around the podium time).
:Code:
	``shootmania:scores``
:Description:
	Teams and players scores.
:Original Callback:
	`Script` Shootmania.Scores

:param players: Player score payload. Including player instance etc.
:param teams: Team score payload.
:param winner_team: The winning team.
:param use_teams: Use teams.
:param winner_player: The winning player.
:param section: Section, current progress of match. Important to check before you save results!!
:type players: list
:type teams: list
"""
