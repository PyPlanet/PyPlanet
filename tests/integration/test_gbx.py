import asynctest

from pyplanet.core.instance import Controller


class TestGbx(asynctest.TestCase):
	async def test_gbx_init(self):
		instance = Controller.prepare(name='default').instance
		await instance.gbx.connect()
		self.assertGreater(len(instance.gbx.gbx_methods), 0)
		await instance.gbx.disconnect()
		del instance

	async def test_gbx_game_infos(self):
		instance = Controller.prepare(name='default').instance
		await instance.gbx.connect()

		assert instance.game.server_player_login is not None
		assert instance.game.dedicated_build is not None
		assert instance.game.dedicated_version is not None
		assert instance.game.dedicated_api_version is not None
		assert instance.game.dedicated_title is not None

		assert instance.game.server_is_dedicated is True
		assert instance.game.server_is_server is True
		assert instance.game.server_ip is not None
		assert instance.game.server_p2p_port is not None
		assert instance.game.server_port is not None
		assert instance.game.server_player_login
		assert instance.game.server_player_id is not None
		assert instance.game.server_download_rate is not None
		assert instance.game.server_upload_rate is not None
		assert instance.game.server_data_dir is not None
		assert instance.game.server_map_dir is not None
		assert instance.game.server_skin_dir is not None
		assert instance.game.game == 'tm' or instance.game.game == 'sm'

		await instance.gbx.disconnect()
		del instance

	async def test_gbx_query(self):
		instance = Controller.prepare(name='default').instance
		await instance.gbx.connect()

		# Direct way.
		version_info = await instance.gbx.execute('GetVersion')
		assert isinstance(version_info, dict)
		assert len(version_info.keys()) > 0

		# Prepared way.
		query = instance.gbx.prepare('GetVersion')
		version_info = await query.execute()
		assert isinstance(version_info, dict)
		assert len(version_info.keys()) > 0

		await instance.gbx.disconnect()
		del instance

	async def test_script_query(self):
		instance = Controller.prepare(name='default').instance
		await instance.gbx.connect()

		# Direct way.
		pause_info = await instance.gbx.script('Maniaplanet.Pause.GetStatus')
		assert isinstance(pause_info, dict)
		assert len(pause_info.keys()) > 0

		# Prepared way.
		query = instance.gbx.prepare('Maniaplanet.Pause.GetStatus')
		pause_info = await query.execute()
		assert isinstance(pause_info, dict)
		assert len(pause_info.keys()) > 0

		await instance.gbx.disconnect()
		del instance

	async def test_multicall(self):
		instance = Controller.prepare(name='default').instance
		await instance.gbx.connect()

		version_info, ladder_info, pause_info = await instance.gbx.multicall(
			instance.gbx.prepare('GetVersion'),
			instance.gbx.prepare('GetLadderServerLimits'),
			instance.gbx.prepare('Maniaplanet.Pause.GetStatus'),  # WARNING: Scripted can't be combined with normal for now.
		)
		assert isinstance(version_info, dict)
		assert len(version_info.keys()) > 0
		assert isinstance(ladder_info, dict)
		assert len(ladder_info.keys()) > 0
		# BECAUSE WE CAN'T COMBINE INSIDE OF MULTICALL. BECAUSE SCRIPTED IS RETURNED AS SCRIPT-CALLBACKS!
		assert pause_info is True

		await instance.gbx.disconnect()
		del instance
