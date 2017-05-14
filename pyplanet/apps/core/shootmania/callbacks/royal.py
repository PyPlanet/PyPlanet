from pyplanet.core import Controller
from pyplanet.core.events import Callback, handle_generic


async def handle_royal_points(source, signal, **kwargs):
	player = Controller.instance.player_manager.get_player(login=source['login'])
	return dict(player=player, type=source['type'], points=source['points'])


player_score_points = Callback(
	call='Script.Shootmania.Royal.Points',
	namespace='shootmania',
	code='royal_player_score_points',
	target=handle_royal_points
)
"""
:Signal: 
	Player score points.
:Code:
	``shootmania:royal_player_score_points``
:Description:
	Callback sent when a player scores some points.
:Original Callback:
	`Script` Shootmania.Royal.Points

:param player: Player instance.
:param type: Type of score, like 'Pole', 'Hit', or 'Survival'.
:param points: Points that the player gains.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


player_spawn = Callback(
	call='Script.Shootmania.Royal.PlayerSpawn',
	namespace='shootmania',
	code='royal_player_spawn',
	target=handle_generic
)
"""
:Signal: 
	Player spawns.
:Code:
	``shootmania:royal_player_spawn``
:Description:
	Callback sent when a player is spawned.
:Original Callback:
	`Script` Shootmania.Royal.PlayerSpawn

:param player: Player instance.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""


results = Callback(
	call='Script.Shootmania.Royal.RoundWinner',
	namespace='shootmania',
	code='royal_results',
	target=handle_generic
)
"""
:Signal: 
	End of round with the winner of the Royal round.
:Code:
	``shootmania:royal_results``
:Description:
	Callback sent at the end of the round with the player instance of the winner.
:Original Callback:
	`Script` Shootmania.Royal.RoundWinner

:param player: Player instance that won the round.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""
