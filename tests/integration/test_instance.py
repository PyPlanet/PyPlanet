import pytest

from pyplanet.core.instance import Controller


@pytest.mark.asyncio
async def test_gbx_init():
	instance = Controller.prepare(name='default').instance
	await instance.gbx.connect()
	assert len(instance.gbx.gbx_methods) > 0
