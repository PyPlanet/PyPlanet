"""
:Victory Types:
	1 = time limit reached, 2 = capture, 3 = attacker eliminated, 4 = defenders eliminated.
"""
import asyncio

from pyplanet.core import Controller
from pyplanet.core.events import Callback

async def handle_elite_turn_start(source, signal, **kwargs):
	attacker = await Controller.instance.player_manager.get_player(login=source['attacker'])
	defenders = await asyncio.gather(*[
		Controller.instance.player_manager.get_player(login=p)
		for p in source['defenders']
	])
	return dict(attacker=attacker, defenders=defenders)

async def handle_elite_turn_end(source, signal, **kwargs):
	return dict(victory_type=source['victorytype'])


turn_start = Callback(
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


turn_end = Callback(
	call='Script.Shootmania.Elite.EndTurn',
	namespace='shootmania',
	code='elite_turn_end',
	target=handle_elite_turn_end
)
"""
:Signal: 
	Elite turn start.
:Code:
	``shootmania:elite_turn_end``
:Description:
	Information about the ending turn.
:Original Callback:
	`Script` Shootmania.Elite.EndTurn

:param victory_type: Describe how the turn was won. 1 = time limit, 2 = capture, 3 = attacker eliminated, 4 = defenders eliminated
"""
