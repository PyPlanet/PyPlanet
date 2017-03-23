from .remote import GbxRemote


class GbxClient(GbxRemote):
	"""
	The GbxClient implements and extends the GbxRemote (very base) with the initializers, special encoders/decoders,
	some fixes/hacks needed for the gbx protocol and some tweaks. This is all to prevent changes from the core
	most important logic `GbxRemote`.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.game = self.instance.game

	async def connect(self):
		await super().connect()
		await self.initialize()

	async def initialize(self):
		"""
		The initialize method will gather information about the server that is only fetched once and saved and used
		in some classes/parts of the application. To make this information available, we use the pyplanet.core.state
		class instance which is a singleton class instance holding information about the server that is public and 
		should be stable. 
		"""
		# Clear the previous created Manialinks.
		await self.query('SendHideManialinkPage')

		# Version Information
		version_info, = await self.query('GetVersion')
		self.game._dedicated_version = version_info['Version']
		self.game._dedicated_build = version_info['Build']
		self.game._dedicated_api_version = version_info['ApiVersion']
		print(self.game.__dict__)
