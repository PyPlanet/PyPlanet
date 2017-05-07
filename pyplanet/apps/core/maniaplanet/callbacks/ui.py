from pyplanet.core import Controller
from pyplanet.core.events import Callback


async def handle_manialink_answer(source, signal, **kwargs):
	_, player_login, action, raw_values = source
	values = dict()
	if isinstance(raw_values, list):
		for val in raw_values:
			values[val['Name']] = val['Value']
	player = await Controller.instance.player_manager.get_player(login=player_login)

	return dict(player=player, action=action, values=values)


manialink_answer = Callback(
	call='ManiaPlanet.PlayerManialinkPageAnswer',
	namespace='maniaplanet',
	code='manialink_answer',
	target=handle_manialink_answer,
)

"""
:Signal: 
	Player has raised an action on the Manialink.
:Code:
	``maniaplanet:manialink_answer``
:Description:
	Callback sent when a player clicks on an event of a manialink.
:Original Callback:
	`Native` Maniaplanet.PlayerManialinkPageAnswer

:param player: Player instance
:param action: Action name
:param values: Values (in dictionary).
:type player: pyplanet.apps.core.maniaplanet.models.player.Player

.. warning ::

	**Don't use this callback directly, use the abstraction of ``View`` and ``StaticManialink`` to handle events of your
	manialink**!

"""

