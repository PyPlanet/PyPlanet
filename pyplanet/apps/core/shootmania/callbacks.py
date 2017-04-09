import asyncio

from pyplanet.apps.core.maniaplanet.models import Player
from pyplanet.core.events import Callback


async def handle_on_shoot(source, signal, **kwargs):
	shooter = await Player.get_by_login(source['shooter'])
	return dict(shooter=shooter, time=source['time'], weapon=source['weapon'])

async def handle_on_hit(source, signal, **kwargs):
	shooter, victim = await asyncio.gather(*[Player.get_by_login(source['shooter']), Player.get_by_login(source['victim'])])
	return dict(
		shooter=shooter, time=source['time'], weapon=source['weapon'], victim=victim, damage=source['damage'],
		shooter_position=source['shooterposition'], victim_position=source['victimposition'],
	)

async def handle_on_near_miss(source, signal, **kwargs):
	shooter, victim = await asyncio.gather(*[Player.get_by_login(source['shooter']), Player.get_by_login(source['victim'])])
	return dict(
		shooter=shooter, time=source['time'], weapon=source['weapon'], victim=victim, distance=source['distance'],
		shooter_position=source['shooterposition'], victim_position=source['victimposition'],
	)

async def handle_armor_empty(source, signal, **kwargs):
	shooter, victim = await asyncio.gather(*[Player.get_by_login(source['shooter']), Player.get_by_login(source['victim'])])
	return dict(
		shooter=shooter, time=source['time'], weapon=source['weapon'], victim=victim,
		shooter_position=source['shooterposition'], victim_position=source['victimposition'],
	)

async def handle_on_capture(source, signal, **kwargs):
	players = await asyncio.gather(*[Player.get_by_login(p) for p in source['players']])
	return dict(time=source['time'], players=players, landmark=source['landmark'])

async def handle_on_shot_deny(source, signal, **kwargs):
	shooter, victim = await asyncio.gather(*[Player.get_by_login(source['shooter']), Player.get_by_login(source['victim'])])
	return dict(
		time=source['time'], shooter=shooter, victim=victim, shooter_weapon=source['shooterweapon'], shooter_victim=source['victimweapon']
	)

async def handle_on_fall_damage(source, signal, **kwargs):
	victim = await Player.get_by_login(source['victim'])
	return dict(time=source['time'], victim=victim)


on_shoot = Callback(
	call='Script.Shootmania.Event.OnShoot',
	namespace='shootmania',
	code='on_shoot',
	target=handle_on_shoot,
)

on_hit = Callback(
	call='Script.Shootmania.Event.OnHit',
	namespace='shootmania',
	code='on_hit',
	target=handle_on_hit,
)

on_near_miss = Callback(
	call='Script.Shootmania.Event.OnNearMiss',
	namespace='shootmania',
	code='on_near_miss',
	target=handle_on_near_miss,
)

on_armor_empty = Callback(
	call='Script.Shootmania.Event.OnArmorEmpty',
	namespace='shootmania',
	code='on_armor_empty',
	target=handle_armor_empty,
)

on_capture = Callback(
	call='Script.Shootmania.Event.OnArmorEmpty',
	namespace='shootmania',
	code='on_capture',
	target=handle_on_capture,
)

on_shot_deny = Callback(
	call='Script.Shootmania.Event.OnShotDeny',
	namespace='shootmania',
	code='on_shot_deny',
	target=handle_on_shot_deny,
)

on_fall_damage = Callback(
	call='Script.Shootmania.Event.OnFallDamage',
	namespace='shootmania',
	code='on_fall_damage',
	target=handle_on_fall_damage,
)

# TODO: Futher implement later.
