from pyplanet.core import Controller
from pyplanet.core.events import Callback


async def handle_manialink_answer(source, signal, **kwargs):
	_, player_login, action, values = source
	player = await Controller.instance.player_manager.get_player(login=player_login)
	return dict(player=player, action=action, values=values)


manialink_answer = Callback(
	call='ManiaPlanet.PlayerManialinkPageAnswer',
	namespace='maniaplanet',
	code='manialink_answer',
	target=handle_manialink_answer,
)
