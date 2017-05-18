import random

from tests.integration import ControllerTestCase


class TestMapManager(ControllerTestCase):

	async def test_map_list(self):
		real_list = await self.instance.gbx.execute('GetMapList', -1, 0)
		assert len(real_list) == len(self.instance.map_manager.maps)

	async def test_map_juke(self):
		if len(self.instance.map_manager.maps) <= 1:
			raise Exception('Test server should contain more than 1 map!')
		while True:
			next_map = random.choice(list(self.instance.map_manager.maps))
			if next_map.uid != self.instance.map_manager.current_map.uid:
				break

		# Set next map
		await self.instance.map_manager.set_next_map(next_map)
		assert self.instance.map_manager.next_map == next_map
		map_info = await self.instance.gbx.execute('GetNextMapInfo')
		assert map_info['UId'] == next_map.uid
	#
	# async def test_map_jump(self):
	# 	if len(self.instance.map_manager.maps) <= 1:
	# 		raise Exception('Test server should contain more than 1 map!')
	# 	while True:
	# 		jump_map = random.choice(self.instance.map_manager.maps)
	# 		if jump_map.uid != self.instance.map_manager.current_map.uid:
	# 			break
	#
	# 	# Skip to next map.
	# 	await self.instance.map_manager.set_current_map(jump_map)
	# 	assert self.instance.map_manager.next_map == jump_map
