import os

TEST_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
TEST_FILES_DIR = os.path.join(TEST_DIR, '_files')

async def drop_tables():
	from pyplanet.core import Controller
	instance = Controller.instance
	if instance and instance.db:
		await instance.db.drop_tables()
