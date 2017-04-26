import asyncio

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.events import Callback, Signal, handle_generic
from pyplanet.core.exceptions import SignalGlueStop


async def handle_start_line(source, signal, **kwargs):
	player = await Player.get_by_login(source['login'])
	flow = player.flow
	flow.start_run()
	return dict(
		player=player, time=source['time'], flow=flow
	)

async def handle_waypoint(source, signal, **kwargs):
	player = await Player.get_by_login(source['login'])
	flow = player.flow

	if not flow.in_run:
		raise SignalGlueStop()

	if not source['isendlap']:
		flow.add_waypoint(source['racetime'])
		return dict(
			player=player, race_time=source['racetime'], flow=flow, raw=source
		)
	elif len(flow.run_cps) >= source['checkpointinlap']:
		# End flow and call the other signal.
		# TODO: Find out if lap or race time is the best to use.
		flow.end_run(source['laptime'])

		await finish.send_robust(source=dict(
			player=player, race_time=source['racetime'], lap_time=source['laptime'], cps=flow.run_cps,
			flow=flow, raw=source
		), raw=True)
	raise SignalGlueStop()

async def handle_give_up(source, signal, **kwargs):
	player = await Player.get_by_login(source['login'])
	player.flow.end_run()
	return dict(player=player, flow=player.flow, time=source['time'])

async def handle_respawn(source, signal, **kwargs):
	player = await Player.get_by_login(source['login'])
	return dict(
		player=player, flow=player.flow, race_cp=source['checkpointinrace'], lap_cp=source['checkpointinlap'],
		race_time=source['racetime'], lap_time=source['laptime']
	)

async def handle_scores(source, signal, **kwargs):
	async def get_player_scores(data):
		player = await Player.get_by_login(data['login'])
		return dict(
			player=player, stunts_score=data['stuntsscore'], best_lap_checkpoints=data['bestlapcheckpoints'],
			match_points=data['match_points'], rank=data['rank'], best_lap_time=data['bestlaptime'],
			best_lap_respawns=data['bestlaprespawns'], map_points=data['mappoints'], best_race_time=data['bestracetime'],
			round_points=data['roundpoints'], best_race_checkpoints=data['bestracecheckpoints'],
			best_race_respawns=data['bestracerespawns']
		)
	async def get_team_scores(data):
		return dict(
			map_points=data['mappoints'], name=data['name'], id=data['id'], match_points=data['matchpoints'],
			round_points=data['roundpoints'],
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


start_line = Callback(
	call='Script.Trackmania.Event.StartLine',
	namespace='trackmania',
	code='start_line',
	target=handle_start_line,
)

start_countdown = Callback(
	call='Script.Trackmania.Event.StartCountdown',
	namespace='trackmania',
	code='start_countdown',
	target=handle_start_line,
)

waypoint = Callback(
	call='Script.Trackmania.Event.WayPoint',
	namespace='trackmania',
	code='waypoint',
	target=handle_waypoint,
)

give_up = Callback(
	call='Script.Trackmania.Event.GiveUp',
	namespace='trackmania',
	code='give_up',
	target=handle_give_up,
)

respawn = Callback(
	call='Script.Trackmania.Event.Respawn',
	namespace='trackmania',
	code='respawn',
	target=handle_respawn,
)

stunt = Callback(
	call='Script.Trackmania.Event.Stunt',
	namespace='trackmania',
	code='stunt',
	target=handle_generic
)

warmup_start = Callback(
	call='Script.Trackmania.WarmUp.Start',
	namespace='trackmania',
	code='warmup_start',
	target=handle_generic
)

warmup_end = Callback(
	call='Script.Trackmania.WarmUp.End',
	namespace='trackmania',
	code='warmup_end',
	target=handle_generic
)

warmup_start_round = Callback(
	call='Script.Trackmania.WarmUp.StartRound',
	namespace='trackmania',
	code='warmup_start_round',
	target=handle_generic
)

warmup_end_round = Callback(
	call='Script.Trackmania.WarmUp.EndRound',
	namespace='trackmania',
	code='warmup_end_round',
	target=handle_generic
)

scores = Callback(
	call='Script.Trackmania.Scores',
	namespace='trackmania',
	code='scores',
	target=handle_scores
)

finish = Signal(
	namespace='trackmania',
	code='finish',
)
