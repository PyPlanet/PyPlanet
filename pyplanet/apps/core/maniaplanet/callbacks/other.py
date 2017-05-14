from pyplanet.core import Controller
from pyplanet.core.events import Callback, handle_generic, Signal


async def handle_bill_updated(source, signal, **kwargs):
	bill_id, state, state_name, transaction_id = source
	return dict(
		bill_id=bill_id, state=state, state_name=state_name, transaction_id=transaction_id
	)

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
	target=handle_bill_updated
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


server_chat = Signal(
	namespace='maniaplanet',
	code='server_chat'
)
"""
:Signal:
	Server send a chat message.
:Code:
	``maniaplanet:server_chat``
:Description:
	Custom signal called when the server outputs a message.
:Origin Callback:
	None (via Chat callback).
"""


channel_progression_start = Callback(
	call='Script.ManiaPlanet.ChannelProgression_Start',
	namespace='maniaplanet',
	code='channel_progression_start',
	target=handle_generic
)
"""
:Signal: 
	Signal sent when channel progression sequence starts.
:Code:
	``maniaplanet:channel_progression_start``
:Description:
	Callback sent when the channel progression sequence starts.
:Original Callback:
	`Script` Maniaplanet.ChannelProgression_Start

:param time: Time when callback has been sent.
"""


channel_progression_end = Callback(
	call='Script.ManiaPlanet.ChannelProgression_End',
	namespace='maniaplanet',
	code='channel_progression_end',
	target=handle_generic
)
"""
:Signal: 
	Signal sent when channel progression sequence ends.
:Code:
	``maniaplanet:channel_progression_end``
:Description:
	Callback sent when the channel progression sequence ends.
:Original Callback:
	`Script` Maniaplanet.ChannelProgression_End

:param time: Time when callback has been sent.
"""
