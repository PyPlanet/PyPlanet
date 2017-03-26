from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.events import Callback, Signal
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


start_line = Callback(
	call='Script.Trackmania.Event.StartLine',
	namespace='trackmania',
	code='start_line',
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

finish = Signal(
	namespace='trackmania',
	code='finish',
)
