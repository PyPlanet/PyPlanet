import asyncio

from tests.integration import ControllerTestCase

#
# class TestPlayerManager(ControllerTestCase):
#
# 	async def test_connect(self):
# 		before_len = len(self.instance.player_manager.online)
#
# 		await self.instance.gbx.execute('ConnectFakePlayer')
# 		await asyncio.sleep(1)
#
# 		after_len = len(self.instance.player_manager.online)
#
# 		assert before_len != after_len
#
# 	async def test_disconnect(self):
# 		before_len = len(self.instance.player_manager.online)
#
# 		name = await self.instance.gbx.execute('ConnectFakePlayer')
# 		await asyncio.sleep(1)
#
# 		after_len = len(self.instance.player_manager.online)
#
# 		await self.instance.gbx.execute('DisconnectFakePlayer', name)
# 		await asyncio.sleep(1)
#
# 		discon_len = len(self.instance.player_manager.online)
#
# 		assert before_len != after_len
