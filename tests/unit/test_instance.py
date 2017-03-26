from pyplanet.core.instance import Controller, Instance


def test_gbx_init():
	instance = Controller.prepare(name='default').instance
	assert isinstance(instance, Instance)
