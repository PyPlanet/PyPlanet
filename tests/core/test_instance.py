import pytest

from pyplanet.core.instance import Instance


@pytest.mark.asyncio
async def test_gbx_init():
	instance = Instance(process_name='default')
	await instance.gbx.connect()
	assert len(instance.gbx.gbx_methods) > 0
