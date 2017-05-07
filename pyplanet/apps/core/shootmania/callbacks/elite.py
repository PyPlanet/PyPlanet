import asyncio

from pyplanet.core import Controller
from pyplanet.core.events import Callback, handle_generic

async def handle_elite_turn_start(source, signal, **kwargs):
	attacker = await Controller.instance.player_manager.get_player(login=source['attacker'])
	defenders = await asyncio.gather(*[
		Controller.instance.player_manager.get_player(login=p)
		for p in source['defenders']
	])
	return dict(attacker=attacker, defenders=defenders)

elite_turn_start = Callback(
	call='Script.Shootmania.Elite.StartTurn',
	namespace='shootmania',
	code='elite_turn_start',
	target=handle_elite_turn_start
)
"""
:Signal: 
	Elite turn start.
:Code:
	``shootmania:elite_turn_start``
:Description:
	Information about the starting turn.
:Original Callback:
	`Script` Shootmania.Elite.StartTurn

:param attacker: Player instance of attacker.
:param defenders: List with player instances of defenders.
:type attacker: pyplanet.apps.core.maniaplanet.models.player.Player
:type defenders: pyplanet.apps.core.maniaplanet.models.player.Player[]
"""
