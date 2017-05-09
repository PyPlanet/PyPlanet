import aiohttp

async def check_latest_version(instance):
	from pyplanet import __version__ as current_version
	from packaging import version

	url = 'https://api.github.com/repos/{}/tags'.format('PyPlanet/PyPlanet')
	async with aiohttp.request('GET', url) as resp:
		latest_name = (await resp.json())[0]['name']
		latest = version.parse(latest_name)
		current = version.parse(current_version)

		if latest > current:
			message = '\uf1e6 $FD4$oPy$369Planet$z$s$fff \uf0e7 new version available: v{}'.format(latest_name)
			await instance.gbx.execute('ChatSendServerMessage', message)
