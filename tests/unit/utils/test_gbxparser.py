import os

import pytest

from pyplanet.utils.gbxparser import GbxParser
from tests import TEST_FILES_DIR


@pytest.mark.asyncio
async def test_gbxparser_map_file():
	parser = GbxParser(file=os.path.join(
		TEST_FILES_DIR,
		'maps',
		'canyon-mp4-1.gbx'
	))

	map_info = await parser.parse()
