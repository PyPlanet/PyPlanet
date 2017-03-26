import asyncio

from pyplanet.core import Controller

async def register_permissions(app):
	perms = Controller.instance.permission_manager
	await asyncio.gather(
		perms.register('use_ok', 'Use the /admin ok (or //ok) command', app=app, min_level=2),
	)
