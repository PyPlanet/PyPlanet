
class _Game:
	"""
	The game class holds information about the game itself and the server. The properties can be virtually overriden
	to be able to proxy to new/old syntaxes. This way we can provide a read-only data structure and still
	maintain the same structure if any of the third party API changes.

	This class is available from the instance with `instance.game`.

	**Most variables seem to contain None, but they actually get propagated during the start and connection
	with the dedicated server**
	"""
	dedicated_build = None
	dedicated_version = None
	dedicated_api_version = None
	dedicated_title = None

	server_is_dedicated = None
	server_is_server = None
	server_is_private = None
	server_ip = None
	server_p2p_port = None
	server_port = None
	server_player_login = None
	server_player_id = None
	server_download_rate = None
	server_upload_rate = None
	server_data_dir = None
	server_map_dir = None
	server_skin_dir = None
	server_language = None
	server_name = None
	server_path = None
	server_password = None
	server_spec_password = None
	server_max_players = None
	server_next_max_players = None
	server_max_specs = None
	server_next_max_specs = None

	ladder_min = None
	ladder_max = None

	game = None  # tm / sm / tmnext

	def game_from_environment(self, environment, game_name=None, title_id=None):
		if game_name == 'Trackmania' and title_id == 'Trackmania':
			return 'tmnext'
		if environment in ['Canyon', 'Stadium', 'Valley', 'Lagoon']:
			return 'tm'
		return 'sm'

	@property
	def game_full(self):
		if self.game == 'tm':
			return 'trackmania'
		elif self.game == 'tmnext':
			return 'trackmania_next'
		return 'shootmania'

Game = _Game()
