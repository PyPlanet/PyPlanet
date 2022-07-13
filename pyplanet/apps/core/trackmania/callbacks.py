import asyncio
import logging

from pyplanet.core import Controller
from pyplanet.core.events import Callback, Signal, handle_generic
from pyplanet.core.exceptions import SignalGlueStop


async def handle_start_line(source, signal, **kwargs):
	player = await Controller.instance.player_manager.get_player(login=source['login'])
	if not player:
		raise SignalGlueStop()
	royal_mode = await Controller.instance.mode_manager.get_current_script() == 'Trackmania/TM_RoyalTimeAttack_Online'
	flow = player.flow
	flow.start_run()

	# TM 2020 Royal Mode.
	if royal_mode:
		flow.handle_start_line_royal(source['time'])

	return dict(
		player=player, time=source['time'], flow=flow
	)


async def handle_waypoint(source, signal, **kwargs):
	player = await Controller.instance.player_manager.get_player(login=source['login'])
	flow = player.flow
	royal_mode = await Controller.instance.mode_manager.get_current_script() == 'Trackmania/TM_RoyalTimeAttack_Online'

	# Custom waypoint handling for TM 2020 Royal Mode.
	if royal_mode and source['isendlap'] and source['isendrace']:
		handled = flow.handle_waypoint_royal(source['racetime'], source['time'], source['blockid'])

		if handled and not len(flow.royal_block_ids) == 5:
			source['isendlap'] = source['isendrace'] = False

			await finish_royal_section.send_robust(source=dict(
				player=player, section_time=flow.royal_section_time, section_nr=len(flow.royal_block_ids),
				block_id=source['blockid'], flow=flow
			), raw=True)
		elif handled and len(flow.royal_block_ids) == 5:
			source['racetime'] = source['laptime'] = flow.royal_total_time
			source['curlapcheckpoints'] = source['curracecheckpoints'] = flow.royal_times

	if not source['isendlap'] and not source['isendrace']:
		return dict(
			player=player, race_time=source['racetime'], flow=flow, raw=source
		)
	elif source['isendlap'] or source['isendrace']:
		# Check if the time is not zero or bellow, if it is, ignore. See #282.
		if source['racetime'] <= 0 or source['laptime'] <= 0:
			raise SignalGlueStop()

		# End flow and call the other signal.
		flow.reset_run()
		if source['isendlap'] and not source['isendrace']:
			flow.start_run()

		await finish.send_robust(source=dict(
			player=player, race_time=source['racetime'], lap_time=source['laptime'],
			cps=source['curlapcheckpoints'], lap_cps=source['curlapcheckpoints'], race_cps=source['curracecheckpoints'],
			flow=flow, is_end_race=source['isendrace'], is_end_lap=source['isendlap'], raw=source,
		), raw=True)

		# Reset royal when driven 5 finishes.
		if royal_mode and len(flow.royal_block_ids) == 5:
			flow.reset_royal(source['time'])
	else:
		logging.warning('Not isendlap!')
	raise SignalGlueStop()


async def handle_give_up(source, signal, **kwargs):
	player = await Controller.instance.player_manager.get_player(login=source['login'])
	flow = player.flow
	royal_mode = await Controller.instance.mode_manager.get_current_script() == 'Trackmania/TM_RoyalTimeAttack_Online'
	flow.reset_run()

	# TM 2020 Royal mode.
	if royal_mode:
		flow.handle_give_up_royal(source['time'])

	return dict(player=player, flow=player.flow, time=source['time'])


async def handle_respawn(source, signal, **kwargs):
	player = await Controller.instance.player_manager.get_player(login=source['login'])
	return dict(
		player=player, flow=player.flow, race_cp=source['checkpointinrace'], lap_cp=source['checkpointinlap'],
		race_time=source['racetime'], lap_time=source['laptime']
	)


async def handle_scores(source, signal, **kwargs):
	async def get_player_scores(data):
		player = await Controller.instance.player_manager.get_player(login=data['login'])
		return dict(
			player=player,
			best_lap_checkpoints=data['bestlapcheckpoints'],
			match_points=data['matchpoints'], rank=data['rank'], best_lap_time=data['bestlaptime'],
			map_points=data['mappoints'], best_race_time=data['bestracetime'],
			round_points=data['roundpoints'], best_race_checkpoints=data['bestracecheckpoints'],

			# TMNext only
			player_account_id=data['accountid'] if 'accountid' in data else None,

			# ManiaPlanet Only (Not for TMNext)
			stunts_score=data['stuntsscore'] if 'stuntsscore' in data else None,
			best_lap_respawns=data['bestlaprespawns'] if 'bestlaprespawns' in data else None,
			best_race_respawns=data['bestracerespawns'] if 'bestracerespawns' in data else None,

			# New since 2.5.0, so check if exist as we want backward compatibility.
			prevracetime=data['prevracetime'] if 'prevracetime' in data else None,
			prevracerespawns=data['prevracerespawns'] if 'prevracerespawns' in data else None,
			prevracecheckpoints=data['prevracecheckpoints'] if 'prevracecheckpoints' in data else None,
			prevstuntsscore=data['prevstuntsscore'] if 'prevstuntsscore' in data else None,
		)

	def get_team_scores(data):
		return dict(
			map_points=data['mappoints'], name=data['name'], id=data['id'], match_points=data['matchpoints'],
			round_points=data['roundpoints'],
		)

	player_scores = await asyncio.gather(*[
		get_player_scores(d) for d in source['players']
	])
	team_scores = [
		get_team_scores(d) for d in source['teams']
	]
	return dict(
		players=player_scores,
		teams=team_scores,
		winner_team=source['winnerteam'],
		use_teams=source['useteams'],
		winner_player=source['winnerplayer'],
		section=source['section']
	)


async def handle_stunt(source, signal, **kwargs):
	player = await Controller.instance.player_manager.get_player(login=source['login'])
	return dict(
		player=player, race_time=source['racetime'], lap_time=source['laptime'], stunt_score=source['stuntsscore'],
		figure=source['figure'], angle=source['angle'], points=source['points'], combo=source['combo'],
		is_straight=source['isstraight'], is_reverse=source['isreverse'], is_master_jump=source['ismasterjump'],
		factor=source['factor']
	)


start_line = Callback(
	call='Script.Trackmania.Event.StartLine',
	namespace='trackmania',
	code='start_line',
	target=handle_start_line,
)
"""
:Signal:
	Player drives off from the start line.
:Code:
	``trackmania:start_line``
:Description:
	Callback sent when a player starts to race (at the end of the 3,2,1,GO! sequence).
:Original Callback:
	`Script` Trackmania.Event.StartLine

:param time: Server time when callback has been sent.
:param player: Player instance
:param flow: Flow class instance.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type flow: pyplanet.apps.core.maniaplanet.models.player.PlayerFlow
"""


start_countdown = Callback(
	call='Script.Trackmania.Event.StartCountdown',
	namespace='trackmania',
	code='start_countdown',
	target=handle_start_line,
)
"""
:Signal:
	Player starts his round, the countdown starts right now.
:Code:
	``trackmania:start_countdown``
:Description:
	Callback sent when a player see the 3,2,1,Go! countdown.
:Original Callback:
	`Script` Trackmania.Event.StartCountdown

:param time: Server time when callback has been sent.
:param player: Player instance
:param flow: Flow class instance.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type flow: pyplanet.apps.core.maniaplanet.models.player.PlayerFlow
"""


waypoint = Callback(
	call='Script.Trackmania.Event.WayPoint',
	namespace='trackmania',
	code='waypoint',
	target=handle_waypoint,
)
"""
:Signal:
	Player crosses a checkpoint.
:Code:
	``trackmania:waypoint``
:Description:
	Callback sent when a player crosses a checkpoint.
:Original Callback:
	`Script` Trackmania.Event.WayPoint

player=player, race_time=source['racetime'], flow=flow, raw=source

:param race_time: Total race time in milliseconds.
:param player: Player instance
:param flow: Flow class instance.
:param raw: Raw data, prevent to use this!
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type flow: pyplanet.apps.core.maniaplanet.models.player.PlayerFlow

.. note ::

	This signal is not called when the player finishes or passes finish line during laps map.

"""


give_up = Callback(
	call='Script.Trackmania.Event.GiveUp',
	namespace='trackmania',
	code='give_up',
	target=handle_give_up,
)
"""
:Signal:
	Player gives up.
:Code:
	``trackmania:give_up``
:Description:
	Callback sent when a player gives up his current run/round.
:Original Callback:
	`Script` Trackmania.Event.GiveUp

:param time: Server time when callback has been sent.
:param player: Player instance
:param flow: Flow class instance.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type flow: pyplanet.apps.core.maniaplanet.models.player.PlayerFlow
"""


respawn = Callback(
	call='Script.Trackmania.Event.Respawn',
	namespace='trackmania',
	code='respawn',
	target=handle_respawn,
)
"""
:Signal:
	Player respawn at cp.
:Code:
	``trackmania:respawn``
:Description:
	Callback sent when a player respawns at the last checkpoint/start.
:Original Callback:
	`Script` Trackmania.Event.Respawn

:param player: Player instance
:param flow: Flow class instance.
:param race_cp: Checkpoint times in current **race**.
:param lap_cp: Checkpoint times in current **lap**.
:param race_time: Total race time in milliseconds.
:param lap_time: Current lap time in milliseconds.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type flow: pyplanet.apps.core.maniaplanet.models.player.PlayerFlow
"""


request_respawn = Callback(
	call='Script.Trackmania.Event.OnPlayerRequestRespawn',
	namespace='trackmania',
	code='request_respawn',
	target=handle_generic,
)
"""
:Signal:
	Request respawn by player.
:Code:
	``trackmania:request_respawn``
:Description:
	Callback sent when a player requests a respawns.
:Original Callback:
	`Script` Trackmania.Event.OnPlayerRequestRespawn

:param login: Player login
:param player: Player instance
:param time: Time of event
:type login: str
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type time: int
"""


stunt = Callback(
	call='Script.Trackmania.Event.Stunt',
	namespace='trackmania',
	code='stunt',
	target=handle_stunt
)
"""
:Signal:
	Player did a stunt.
:Code:
	``trackmania:stunt``
:Description:
	Callback sent when a player did a stunt.
:Original Callback:
	`Script` Trackmania.Event.Stunt

:param player: Player instance
:param race_time: Total race time in milliseconds.
:param lap_time: Current lap time in milliseconds.
:param stunt_score: Current stunt score.
:param figure: Figure of stunt.
:param angle: Angle of stunt.
:param points: Points got by figure.
:param combo: Combo counter
:param is_straight: Is the jump/stunt straight.
:param is_reverse: Is jump/stunt reversed.
:param is_master_jump: Is master jump.
:param factor: Factor multiplier of points (figure).
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


warmup_start = Callback(
	call='Script.Trackmania.WarmUp.Start',
	namespace='trackmania',
	code='warmup_start',
	target=handle_generic
)
"""
:Signal:
	Warmup Starts
:Code:
	``trackmania:warmup_start``
:Description:
	Callback sent when the warmup starts.
:Original Callback:
	`Script` Trackmania.WarmUp.Start
"""


warmup_end = Callback(
	call='Script.Trackmania.WarmUp.End',
	namespace='trackmania',
	code='warmup_end',
	target=handle_generic
)
"""
:Signal:
	Warmup Ends
:Code:
	``trackmania:warmup_end``
:Description:
	Callback sent when the warmup ends.
:Original Callback:
	`Script` Trackmania.WarmUp.End
"""


warmup_start_round = Callback(
	call='Script.Trackmania.WarmUp.StartRound',
	namespace='trackmania',
	code='warmup_start_round',
	target=handle_generic
)
"""
:Signal:
	Warmup Round Starts.
:Code:
	``trackmania:warmup_start_round``
:Description:
	Callback sent when a warm up round start.
:Original Callback:
	`Script` Trackmania.WarmUp.StartRound

:param current: Current round number.
:param total: Total warm up rounds.
"""


warmup_end_round = Callback(
	call='Script.Trackmania.WarmUp.EndRound',
	namespace='trackmania',
	code='warmup_end_round',
	target=handle_generic
)
"""
:Signal:
	Warmup Round Ends.
:Code:
	``trackmania:warmup_end_round``
:Description:
	Callback sent when a warm up round ends.
:Original Callback:
	`Script` Trackmania.WarmUp.EndRound

:param current: Current round number.
:param total: Total warm up rounds.
"""


scores = Callback(
	call='Script.Trackmania.Scores',
	namespace='trackmania',
	code='scores',
	target=handle_scores
)
"""
:Signal:
	Score callback, called after the map. (Around the podium time).
:Code:
	``trackmania:scores``
:Description:
	Teams and players scores.
:Original Callback:
	`Script` Trackmania.Scores

:param players: Player score payload. Including player instance etc.
:param teams: Team score payload.
:param winner_team: The winning team.
:param use_teams: Use teams.
:param winner_player: The winning player.
:param section: Section, current progress of match. Important to check before you save results!!
:type players: list
:type teams: list
"""


finish = Signal(
	namespace='trackmania',
	code='finish',
)
"""
:Signal:
	Player finishes a lap or the race.
:Code:
	``trackmania:finish``
:Description:
	Player finishes a lap or the complete race. Custom signal!.
:Original Callback:
	*None*

:param player: Player instance.
:param race_time: Time in milliseconds of the complete race.
:param lap_time: Time in milliseconds of the current lap.
:param cps: Deprecated!
:param lap_cps: Current lap checkpoint times.
:param race_cps: Complete race checkpoint times.
:param flow: Flow instance.
:param is_end_race: Is this the finish and end of race.
:param is_end_lap: Is this the finish and end of current lap.
:param raw: Prevent to use this!
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type flow: pyplanet.apps.core.maniaplanet.models.player.PlayerFlow
:type race_time: int
:type lap_time: int
:type lap_cps: list
:type race_cps: list
:type is_end_race: bool
:type is_end_lap: bool
"""


finish_royal_section = Signal(
	namespace='trackmania',
	code='finish_royal_section',
)
"""
:Signal:
	Player finishes a section of a royal map. (it will also fire waypoint!)
:Code:
	``trackmania:finish_royal_section``
:Description:
	Player finishes a section of a royal map. Custom signal!.
:Original Callback:
	*None*

:param player: Player instance.
:param section_time: Time in milliseconds of the complete race.
:param section_nr: The section number.
:param block_id: Block ID.
:param flow: Flow instance.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
:type flow: pyplanet.apps.core.maniaplanet.models.player.PlayerFlow
:type section_time: int
:type section_nr: int
:type block_id: any
"""


warmup_status = Callback(
	call='Script.Trackmania.WarmUp.Status',
	namespace='trackmania',
	code='warmup_status',
	target=handle_generic
)
"""
:Signal:
	Status of Trackmania warmup. (mostly as response).
:Code:
	``trackmania:warmup_status``
:Description:
	The status of Trackmania's the warmup.
:Original Callback:
	`Script` Trackmania.WarmUp.Status

:param responseid: Internally used. Ignore
:param available: Is warmup available in the game mode. (Boolean).
:param active: Is warmup active and ongoing right now.
:type available: bool
:type active: bool
"""


tmnext_properties = Callback(
	call='Script.Common.UIModules.Properties',
	namespace='trackmania',
	code='common_uimodules_properties',
	target=handle_generic
)
"""
:Signal:
	Common.UIModules.Properties for TM2020
:Code:
	``trackmania:common_uimodules_properties``
:Description:
	Returns UIModules Properties like for instance: Race_Chrono see: ``[{'id': 'Race_Chrono', 'position': [0, -80], 'scale': 1, 'visible': True},``
:Original Callback:
	`Script` Common.UIModules.Properties

:param responseid: Internally used. Ignore
:param uimodules: Collection of all UIModules in TM2020.
:type id Name of the UIModule
:type position Position to place/get Position [0,-80] as example
:type scale Scale measurement
:type visible Boolean True or False
"""


tmnext_ko_elimination = Callback(
	call='Script.Trackmania.Knockout.Elimination',
	namespace='trackmania',
	code='tmnext_ko_elimination',
	target=handle_generic
)
"""
:Signal:
	Knockout Elimination Callback.
:Code:
	``trackmania:knockout_Elimination``
:Description:
	Returns a webserviceId on Player Knockout.
:Original Callback:
	`Script` Trackmania.Knockout.Elimination

:param responseid: Internally used. Ignore
:param account-id: example: ab6fa572-48d7-4b16-a2d7-5c760a05f97b.

"""
