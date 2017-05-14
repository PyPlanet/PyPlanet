from pyplanet.core import Controller
from pyplanet.core.events import Callback, handle_generic


async def handle_map_loading(source, signal, **kwargs):
	map = await Controller.instance.map_manager.get_map(uid=source['map']['uid'])
	return dict(
		map=map,
		restarted=source.get('restarted', None),
	)


server_start = Callback(
	call='Script.Maniaplanet.StartServer_Start',
	namespace='maniaplanet',
	code='server_start',
	target=handle_generic,
)
"""
:Signal: 
	Server Start signal
:Code:
	``maniaplanet:server_start``
:Description:
	This callback is called when the server script is (re)started. The begin of the event.
:Original Callback:
	`Script` Maniaplanet.StartServer_Start

:param restarted: Boolean giving information if the script has restarted.
:param time: Server time when callback has been sent.
"""


server_start__end = Callback(
	call='Script.Maniaplanet.StartServer_End',
	namespace='maniaplanet',
	code='server_start__end',
	target=handle_generic,
)
"""
:Signal: 
	Server Start signal (end of event).
:Code:
	``maniaplanet:server_start__end``
:Description:
	This callback is called when the server script is (re)started. The end of the event.
:Original Callback:
	`Script` Maniaplanet.StartServer_End

:param restarted: Boolean giving information if the script has restarted.
:param time: Server time when callback has been sent.
"""


server_end = Callback(
	call='Script.Maniaplanet.EndServer_Start',
	namespace='maniaplanet',
	code='server_end',
	target=handle_generic,
)
"""
:Signal: 
	Server End signal
:Code:
	``maniaplanet:server_end``
:Description:
	This callback is called when the server script is end. The begin of the event.
:Original Callback:
	`Script` Maniaplanet.EndServer_Start

:param restarted: Boolean giving information if the script has restarted.
:param time: Server time when callback has been sent.
"""


server_end__end = Callback(
	call='Script.Maniaplanet.EndServer_End',
	namespace='maniaplanet',
	code='server_end__end',
	target=handle_generic,
)
"""
:Signal: 
	Server End signal (end event)
:Code:
	``maniaplanet:server_end__end``
:Description:
	This callback is called when the server script is end. The end of the event.
:Original Callback:
	`Script` Maniaplanet.EndServer_End

:param restarted: Boolean giving information if the script has restarted.
:param time: Server time when callback has been sent.
"""


match_start = Callback(
	call='Script.Maniaplanet.StartMatch_Start',
	namespace='maniaplanet',
	code='match_start',
	target=handle_generic,
)
"""
:Signal: 
	Match Start.
:Code:
	``maniaplanet:match_start``
:Description:
	Callback sent when the "StartMatch" section start.
:Original Callback:
	`Script` Maniaplanet.StartMatch_Start

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


match_start__end = Callback(
	call='Script.Maniaplanet.StartMatch_End',
	namespace='maniaplanet',
	code='match_start__end',
	target=handle_generic,
)
"""
:Signal: 
	Match Start. (End event)
:Code:
	``maniaplanet:match_start__end``
:Description:
	Callback sent when the "StartMatch" section end.
:Original Callback:
	`Script` Maniaplanet.StartMatch_End

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


match_end = Callback(
	call='Script.Maniaplanet.EndMatch_Start',
	namespace='maniaplanet',
	code='match_end',
	target=handle_generic,
)
"""
:Signal: 
	Match End.
:Code:
	``maniaplanet:match_end``
:Description:
	Callback sent when the "EndMatch" section start.
:Original Callback:
	`Script` Maniaplanet.EndMatch_Start

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


match_end__end = Callback(
	call='Script.Maniaplanet.EndMatch_End',
	namespace='maniaplanet',
	code='match_end__end',
	target=handle_generic,
)
"""
:Signal: 
	Match End. (End event)
:Code:
	``maniaplanet:match_end__end``
:Description:
	Callback sent when the "EndMatch" section ends.
:Original Callback:
	`Script` Maniaplanet.EndMatch_End

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


round_start = Callback(
	call='Script.Maniaplanet.StartRound_Start',
	namespace='maniaplanet',
	code='round_start',
	target=handle_generic,
)
"""
:Signal: 
	Round Start.
:Code:
	``maniaplanet:round_start``
:Description:
	Callback sent when the "StartRound" section starts.
:Original Callback:
	`Script` Maniaplanet.StartRound_Start

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


round_start__end = Callback(
	call='Script.Maniaplanet.StartRound_End',
	namespace='maniaplanet',
	code='round_start__end',
	target=handle_generic,
)
"""
:Signal: 
	Round Start. (End event)
:Code:
	``maniaplanet:round_start__end``
:Description:
	Callback sent when the "StartRound" section ends.
:Original Callback:
	`Script` Maniaplanet.StartRound_End

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


round_end = Callback(
	call='Script.Maniaplanet.EndRound_Start',
	namespace='maniaplanet',
	code='round_end',
	target=handle_generic,
)
"""
:Signal: 
	Round Start.
:Code:
	``maniaplanet:round_end``
:Description:
	Callback sent when the "EndRound" section starts.
:Original Callback:
	`Script` Maniaplanet.EndRound_Start

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


round_end__end = Callback(
	call='Script.Maniaplanet.EndRound_End',
	namespace='maniaplanet',
	code='round_end__end',
	target=handle_generic,
)
"""
:Signal: 
	Round Start. (End event)
:Code:
	``maniaplanet:round_end__end``
:Description:
	Callback sent when the "EndRound" section ends.
:Original Callback:
	`Script` Maniaplanet.EndRound_End

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


turn_start = Callback(
	call='Script.Maniaplanet.StartTurn_Start',
	namespace='maniaplanet',
	code='turn_start',
	target=handle_generic,
)
"""
:Signal: 
	Turn Start.
:Code:
	``maniaplanet:turn_start``
:Description:
	Callback sent when the "StartTurn" section starts.
:Original Callback:
	`Script` Maniaplanet.StartTurn_Start

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


turn_start__end = Callback(
	call='Script.Maniaplanet.StartTurn_End',
	namespace='maniaplanet',
	code='turn_start__end',
	target=handle_generic,
)
"""
:Signal: 
	Turn Start. (End event).
:Code:
	``maniaplanet:turn_start__end``
:Description:
	Callback sent when the "StartTurn" section ends.
:Original Callback:
	`Script` Maniaplanet.StartTurn_End

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


turn_end = Callback(
	call='Script.Maniaplanet.EndTurn_Start',
	namespace='maniaplanet',
	code='turn_end',
	target=handle_generic,
)
"""
:Signal: 
	Turn End.
:Code:
	``maniaplanet:turn_end``
:Description:
	Callback sent when the "EndTurn" section starts.
:Original Callback:
	`Script` Maniaplanet.EndTurn_Start

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


turn_end__end = Callback(
	call='Script.Maniaplanet.EndTurn_End',
	namespace='maniaplanet',
	code='turn_end__end',
	target=handle_generic,
)
"""
:Signal: 
	Turn End. (End event)
:Code:
	``maniaplanet:turn_end__end``
:Description:
	Callback sent when the "EndTurn" section ends.
:Original Callback:
	`Script` Maniaplanet.EndTurn_End

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


play_loop_start = Callback(
	call='Script.Maniaplanet.StartPlayLoop',
	namespace='maniaplanet',
	code='play_loop_start',
	target=handle_generic,
)
"""
:Signal: 
	Play Loop Start.
:Code:
	``maniaplanet:play_loop_start``
:Description:
	Callback sent when the "PlayLoop" section starts.
:Original Callback:
	`Script` Maniaplanet.StartPlayLoop

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


play_loop_end = Callback(
	call='Script.Maniaplanet.EndPlayLoop',
	namespace='maniaplanet',
	code='play_loop_end',
	target=handle_generic,
)
"""
:Signal: 
	Play Loop End.
:Code:
	``maniaplanet:play_loop_end``
:Description:
	Callback sent when the "PlayLoop" section ends.
:Original Callback:
	`Script` Maniaplanet.EndPlayLoop

:param count: Each time this section is played, this number is incremented by one.
:param time: Server time when callback has been sent.
"""


loading_map_start = Callback(
	call='Script.Maniaplanet.LoadingMap_Start',
	namespace='maniaplanet',
	code='loading_map_start',
	target=handle_generic
)
"""
:Signal: 
	Loading Map start.
:Code:
	``maniaplanet:loading_map_start``
:Description:
	Callback sent when the server starts loading the map.
:Original Callback:
	`Script` Maniaplanet.LoadingMap_Start

:param time: Server time when callback has been sent.
"""


loading_map_end = Callback(
	call='Script.Maniaplanet.LoadingMap_End',
	namespace='maniaplanet',
	code='loading_map_end',
	target=handle_map_loading
)
"""
:Signal: 
	Loading Map end.
:Code:
	``maniaplanet:loading_map_end``
:Description:
	Callback sent when the server finishes to load the map.
:Original Callback:
	`Script` Maniaplanet.LoadingMap_End

:param map: Map instance from database. Updated with the provided data.
:type map: pyplanet.core.maniaplanet.models.map.Map
"""


unloading_map_start = Callback(
	call='Script.Maniaplanet.UnloadingMap_Start',
	namespace='maniaplanet',
	code='unloading_map_start',
	target=handle_map_loading
)
"""
:Signal: 
	Unloading of the Map starts.
:Code:
	``maniaplanet:unloading_map_start``
:Description:
	Callback sent when the server starts to unload a map.
:Original Callback:
	`Script` Maniaplanet.UnloadingMap_Start

:param map: Map instance from database. Updated with the provided data.
:type map: pyplanet.core.maniaplanet.models.map.Map
"""


unloading_map_end = Callback(
	call='Script.Maniaplanet.UnloadingMap_End',
	namespace='maniaplanet',
	code='unloading_map_end',
	target=handle_generic
)
"""
:Signal: 
	Unloading of the Map ends.
:Code:
	``maniaplanet:unloading_map_end``
:Description:
	Callback sent when the server finishes to unload a map.
:Original Callback:
	`Script` Maniaplanet.UnloadingMap_End

:param map: Map instance from database. Updated with the provided data.
:type map: pyplanet.core.maniaplanet.models.map.Map
"""


podium_start = Callback(
	call='Script.Maniaplanet.Podium_Start',
	namespace='maniaplanet',
	code='podium_start',
	target=handle_generic
)
"""
:Signal: 
	Podium start.
:Code:
	``maniaplanet:podium_start``
:Description:
	Callback sent when the podium sequence starts.
:Original Callback:
	`Script` Maniaplanet.Podium_Start

:param time: Server time when callback has been sent.
"""


podium_end = Callback(
	call='Script.Maniaplanet.Podium_End',
	namespace='maniaplanet',
	code='podium_end',
	target=handle_generic
)
"""
:Signal: 
	Podium end.
:Code:
	``maniaplanet:podium_end``
:Description:
	Callback sent when the podium sequence ends.
:Original Callback:
	`Script` Maniaplanet.Podium_End

:param time: Server time when callback has been sent.
"""


match_begin = Callback(
	call='ManiaPlanet.BeginMatch',
	namespace='maniaplanet',
	code='match_begin',
	target=handle_generic,
)
match_stop = Callback(
	call='ManiaPlanet.EndMatch',
	namespace='maniaplanet',
	code='match_stop',
	target=handle_generic,
)


status_changed = Callback(
	call='ManiaPlanet.StatusChanged',
	namespace='maniaplanet',
	code='status_changed',
	target=handle_generic,
)
"""
:Signal: 
	Server Status Changed.
:Code:
	``maniaplanet:status_changed``
:Description:
	Callback sent when the podium sequence ends.
:Original Callback:
	`Native` Maniaplanet.Podium_End

:param 1: Status Code.
:param 2: Status Name.
:type 1: int
:type 2: str
"""
