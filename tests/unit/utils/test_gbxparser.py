import os
import asynctest

from pyplanet.utils.gbxparser import GbxParser
from tests import TEST_FILES_DIR


class TestGbxParser(asynctest.TestCase):

	@asynctest.fail_on(unused_loop=False)
	async def test_gbxparser_map_file(self):
		parser = GbxParser(file=os.path.join(
			TEST_FILES_DIR,
			'maps',
			'greyroad.gbx'
		))

		map_info = await parser.parse()

		assert map_info['time_bronze'] == 72000
		assert map_info['time_silver'] == 57000
		assert map_info['time_gold'] == 51000
		assert map_info['time_author'] == 47488

		assert map_info['uid'] == '46Yh0hgv5EdSb6IkHsYK1PXHaua'
		assert map_info['name'] == '$s$678$oGrey$o$fff road'
		assert map_info['price'] == 5135
		assert map_info['is_multilap'] == False
		assert map_info['map_type'] == 'Trackmania\\Race'
		assert map_info['map_style'] == ''
		assert map_info['editor'] == 'advanced'
		assert map_info['checkpoints'] == 11
		assert map_info['laps'] == 1

		assert map_info['author_login'] == 'tomvalk'
		assert map_info['author_score'] == 47488
		assert map_info['author_version'] == 0
		assert map_info['author_nickname'] == '$f80$i$s$o$h[maniaflash?toffe]Toffe$z$06fSmurf'
		assert map_info['author_extra'] == ''

		assert map_info['environment'] == 'Canyon'
		assert map_info['title_id'] == 'TMCanyon'
		assert map_info['mood'] == 'Sunrise'

	@asynctest.fail_on(unused_loop=False)
	async def test_gbxparser_map_buffer(self):
		buffer = open(os.path.join(
			TEST_FILES_DIR,
			'maps',
			'greyroad.gbx'
		), mode='rb')
		parser = GbxParser(buffer=buffer)

		map_info = await parser.parse()

		assert map_info['time_bronze'] == 72000
		assert map_info['time_silver'] == 57000
		assert map_info['time_gold'] == 51000
		assert map_info['time_author'] == 47488

		assert map_info['uid'] == '46Yh0hgv5EdSb6IkHsYK1PXHaua'
		assert map_info['name'] == '$s$678$oGrey$o$fff road'
		assert map_info['price'] == 5135
		assert map_info['is_multilap'] == False
		assert map_info['map_type'] == 'Trackmania\\Race'
		assert map_info['map_style'] == ''
		assert map_info['editor'] == 'advanced'
		assert map_info['checkpoints'] == 11
		assert map_info['laps'] == 1

		assert map_info['author_login'] == 'tomvalk'
		assert map_info['author_score'] == 47488
		assert map_info['author_version'] == 0
		assert map_info['author_nickname'] == '$f80$i$s$o$h[maniaflash?toffe]Toffe$z$06fSmurf'
		assert map_info['author_extra'] == ''

		assert map_info['environment'] == 'Canyon'
		assert map_info['title_id'] == 'TMCanyon'
		assert map_info['mood'] == 'Sunrise'
