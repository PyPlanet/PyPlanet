from pyplanet.core import Controller
from pyplanet.core.events import Callback, handle_generic


async def handle_map_loading(source, signal, **kwargs):
	map = await Controller.instance.map_manager.get_map(uid=source['map']['uid'])
	return dict(
		map=map,
	)


server_start = Callback(
	call='Script.Maniaplanet.StartServer_Start',
	namespace='maniaplanet',
	code='server_start',
	target=handle_generic,
)
server_start__end = Callback(
	call='Script.Maniaplanet.StartServer_End',
	namespace='maniaplanet',
	code='server_start__end',
	target=handle_generic,
)
server_end = Callback(
	call='Script.Maniaplanet.EndServer_Start',
	namespace='maniaplanet',
	code='server_end',
	target=handle_generic,
)
server_end__end = Callback(
	call='Script.Maniaplanet.EndServer_End',
	namespace='maniaplanet',
	code='server_end__end',
	target=handle_generic,
)

match_start = Callback(
	call='Script.Maniaplanet.StartMatch_Start',
	namespace='maniaplanet',
	code='match_start',
	target=handle_generic,
)
match_start__end = Callback(
	call='Script.Maniaplanet.StartMatch_End',
	namespace='maniaplanet',
	code='match_start__end',
	target=handle_generic,
)
match_end = Callback(
	call='Script.Maniaplanet.EndMatch_Start',
	namespace='maniaplanet',
	code='match_end',
	target=handle_generic,
)
match_end__end = Callback(
	call='Script.Maniaplanet.EndMatch_End',
	namespace='maniaplanet',
	code='match_end__end',
	target=handle_generic,
)

round_start = Callback(
	call='Script.Maniaplanet.StartRound_Start',
	namespace='maniaplanet',
	code='round_start',
	target=handle_generic,
)
round_start__end = Callback(
	call='Script.Maniaplanet.StartRound_End',
	namespace='maniaplanet',
	code='round_start__end',
	target=handle_generic,
)
round_end = Callback(
	call='Script.Maniaplanet.EndRound_Start',
	namespace='maniaplanet',
	code='round_end',
	target=handle_generic,
)
round_end__end = Callback(
	call='Script.Maniaplanet.EndRound_End',
	namespace='maniaplanet',
	code='round_end__end',
	target=handle_generic,
)

turn_start = Callback(
	call='Script.Maniaplanet.StartTurn_Start',
	namespace='maniaplanet',
	code='turn_start',
	target=handle_generic,
)
turn_start__end = Callback(
	call='Script.Maniaplanet.StartTurn_End',
	namespace='maniaplanet',
	code='turn_start__end',
	target=handle_generic,
)
turn_end = Callback(
	call='Script.Maniaplanet.EndTurn_Start',
	namespace='maniaplanet',
	code='turn_end',
	target=handle_generic,
)
turn_end__end = Callback(
	call='Script.Maniaplanet.EndTurn_End',
	namespace='maniaplanet',
	code='turn_end__end',
	target=handle_generic,
)

play_loop_start = Callback(
	call='Script.Maniaplanet.StartPlayLoop',
	namespace='maniaplanet',
	code='play_loop_start',
	target=handle_generic,
)
play_loop_end = Callback(
	call='Script.Maniaplanet.EndPlayLoop',
	namespace='maniaplanet',
	code='play_loop_end',
	target=handle_generic,
)

loading_map_start = Callback(
	call='Script.Maniaplanet.LoadingMap_Start',
	namespace='maniaplanet',
	code='loading_map_start',
	target=handle_generic
)
loading_map_end = Callback(
	call='Script.Maniaplanet.LoadingMap_End',
	namespace='maniaplanet',
	code='loading_map_start',
	target=handle_map_loading
)

unloading_map_start = Callback(
	call='Script.Maniaplanet.UnloadingMap_Start',
	namespace='maniaplanet',
	code='unloading_map_start',
	target=handle_map_loading
)
unloading_map_end = Callback(
	call='Script.Maniaplanet.UnloadingMap_End',
	namespace='maniaplanet',
	code='unloading_map_end',
	target=handle_generic
)

podium_start = Callback(
	call='Script.Maniaplanet.Podium_Start',
	namespace='maniaplanet',
	code='podium_start',
	target=handle_generic
)
podium_end = Callback(
	call='Script.Maniaplanet.Podium_End',
	namespace='maniaplanet',
	code='podium_end',
	target=handle_generic
)

match_begin = Callback(
	call='ManiaPlanet.BeginMatch',
	namespace='maniaplanet',
	code='match_begin',
	target=handle_generic,
)

status_changed = Callback(
	call='ManiaPlanet.StatusChanged',
	namespace='maniaplanet',
	code='status_changed',
	target=handle_generic,
)
