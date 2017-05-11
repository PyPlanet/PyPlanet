from pyplanet.core.events import Callback, handle_generic
from pyplanet.core.instance import Controller


async def handle_map_begin(source, signal, **kwargs):
	# Retrieve and update map, return it to our callback listeners.
	map = await Controller.instance.map_manager.handle_map_change(source)
	return dict(map=map)

async def handle_map_end(source, signal, **kwargs):
	# Retrieve and update map, return it to our callback listeners.
	map = await Controller.instance.map_manager.handle_map_change(source)
	return dict(map=map)

async def handle_playlist_modified(source, signal, **kwargs):
	# Make sure the map manager fetches the updated maplist.
	updated = await Controller.instance.map_manager.handle_playlist_change(source)
	if not isinstance(source, dict):
		source = dict()
	source['maps_updated'] = updated
	return source

async def handle_map_start(source, signal, **kwargs):
	# Get the map
	map = await Controller.instance.map_manager.get_map(source['map']['uid'])
	return dict(
		time=source['time'], count=source['count'], restarted=source['restarted'], map=map,
	)


# We don't use scripted map events due to the information we get and the stability of the information structure.
map_begin = Callback(
	call='ManiaPlanet.BeginMap',
	namespace='maniaplanet',
	code='map_begin',
	target=handle_map_begin,
)
"""
:Signal: 
	Begin of map.
:Code:
	``maniaplanet:map_begin``
:Description:
	Callback sent when map begins.
:Original Callback:
	`Native` Maniaplanet.BeginMap

:param map: Map instance.
:type map: pyplanet.apps.core.maniaplanet.models.map.Map
"""

map_end = Callback(
	call='ManiaPlanet.EndMap',
	namespace='maniaplanet',
	code='map_end',
	target=handle_map_end,
)
"""
:Signal: 
	End of map.
:Code:
	``maniaplanet:map_end``
:Description:
	Callback sent when map ends.
:Original Callback:
	`Native` Maniaplanet.EndMap

:param map: Map instance.
:type map: pyplanet.apps.core.maniaplanet.models.map.Map
"""

playlist_modified = Callback(
	call='ManiaPlanet.MapListModified',
	namespace='maniaplanet',
	code='playlist_modified',
	target=handle_playlist_modified
)
"""
:Signal: 
	Maplist changes.
:Code:
	``maniaplanet:playlist_modified``
:Description:
	Callback sent when map list changes.
:Original Callback:
	`Native` Maniaplanet.MapListModified

:param 1: Current map index.
:param 2: Next map index.
:param 3: Is List Modified.
:type 1: int
:type 2: int
:type 3: bool
"""

map_start = Callback(
	call='Script.Maniaplanet.StartMap_Start',
	namespace='maniaplanet',
	code='map_start',
	target=handle_map_start
)
"""
:Signal: 
	Begin of map. (Scripted!)
:Code:
	``maniaplanet:map_begin``
:Description:
	Callback sent when map starts (same as begin, but scripted).
:Original Callback:
	`Script` Maniaplanet.StartMap_Start

:param time: Time when callback has been sent.
:param count: Counts of the callback that was sent.
:param restarted: Is the map restarted.
:param map: Map instance.
:type map: pyplanet.apps.core.maniaplanet.models.map.Map
"""

map_start__end = Callback(
	call='Script.Maniaplanet.StartMap_End',
	namespace='maniaplanet',
	code='map_start__end',
	target=handle_map_start
)
"""
:Signal: 
	Begin of map, end of event. (Scripted!)
:Code:
	``maniaplanet:map_start__end``
:Description:
	Callback sent when map starts (same as begin, but scripted). End of the event
:Original Callback:
	`Script` Maniaplanet.StartMap_End

:param time: Time when callback has been sent.
:param count: Counts of the callback that was sent.
:param restarted: Is the map restarted.
:param map: Map instance.
:type map: pyplanet.apps.core.maniaplanet.models.map.Map
"""

