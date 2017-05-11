import asyncio

from pyplanet.core import Controller
from pyplanet.core.events import Callback, handle_generic


async def handle_joust_selected_players(source, signal, **kwargs):
	players = await asyncio.gather(*[
		Controller.instance.player_manager.get_player(login=p)
		for p in source['players']
	])
	return dict(players=players)

async def handle_joust_results(source, signal, **kwargs):
	async def get_player_result(data):
		player = await Controller.instance.player_manager.get_player(login=data['login'])
		return dict(player=player, score=data['score'])
	players = await asyncio.gather(*[
		get_player_result(d) for d in source['players']
	])
	return dict(players=players)


player_reload = Callback(
	call='Script.Shootmania.Joust.OnReload',
	namespace='shootmania',
	code='joust_player_reload',
	target=handle_generic
)
"""
:Signal: 
	Player reloads its weapon and capture pole.
:Code:
	``shootmania:joust_player_reload``
:Description:
	Callback sent when a player capture a pole to reload its weapons.
:Original Callback:
	`Script` Shootmania.Joust.OnReload

:param login: Player login.
:param player: Player instance.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


selected_players = Callback(
	call='Script.Shootmania.Joust.SelectedPlayers',
	namespace='shootmania',
	code='joust_selected_players',
	target=handle_joust_selected_players
)
"""
:Signal: 
	Round starts with selected players.
:Code:
	``shootmania:joust_selected_players``
:Description:
	Callback sent at the beginning of the round with the logins of the players selected to play the round.
:Original Callback:
	`Script` Shootmania.Joust.SelectedPlayers

:param players: Player list (instances).
:type players: pyplanet.apps.core.maniaplanet.models.player.Player[]
"""


results = Callback(
	call='Script.Shootmania.Joust.RoundResult',
	namespace='shootmania',
	code='joust_results',
	target=handle_joust_results
)
"""
:Signal: 
	End of round with results of Joust round.
:Code:
	``shootmania:joust_results``
:Description:
	Callback sent at the end of the round with the scores of the two players.
:Original Callback:
	`Script` Shootmania.Joust.RoundResult

:param players: Player score list, contains player + score.
:type players: list
"""
