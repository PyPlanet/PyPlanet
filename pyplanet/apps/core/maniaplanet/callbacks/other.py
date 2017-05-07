from pyplanet.core import Controller
from pyplanet.core.events import Callback, handle_generic


async def handle_vote_updated(source, signal, **kwargs):
	state, login, cmd_name, cmd_param = source
	player = await Controller.instance.player_manager.get_player(login)
	return dict(
		player=player, state=state, cmd_name=cmd_name, cmd_param=cmd_param
	)


bill_updated = Callback(
	call='ManiaPlanet.BillUpdated',
	namespace='maniaplanet',
	code='bill_updated',
	target=handle_generic
)
"""
:Signal: 
	Bill has been updated.
:Code:
	``maniaplanet:bill_updated``
:Description:
	Callback sent when a bill has been updated.
:Original Callback:
	`Native` Maniaplanet.BillUpdated

:param 1: Bill id.
:param 2: State.
:param 3: State name.
:param 4: Transaction id.
:type 1: int
:type 2: int
:type 3: str
:type 4: int
"""

vote_updated = Callback(
	call='ManiaPlanet.VoteUpdated',
	namespace='maniaplanet',
	code='vote_updated',
	target=handle_vote_updated
)
"""
:Signal: 
	Vote has been updated.
:Code:
	``maniaplanet:vote_updated``
:Description:
	Callback sent when a call vote has been updated.
:Original Callback:
	`Native` Maniaplanet.VoteUpdated

:param player: Player instance
:param state: State name
:param cmd_name: Command name
:param cmd_param: Parameter given with command.
:type player: pyplanet.apps.core.maniaplanet.models.player.Player
"""
