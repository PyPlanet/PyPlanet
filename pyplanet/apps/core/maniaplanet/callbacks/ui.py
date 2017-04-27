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
