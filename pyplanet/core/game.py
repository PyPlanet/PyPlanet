
class _Game:
	"""
	The game class holds information about the game itself and the server. The properties can be virtually overriden
	to be able to proxy to new/old syntaxes. This way we can provide a read-only data structure and still
	maintain the same structure if any of the third party API changes.  
	"""
	dedicated_build = None
	dedicated_version = None
	dedicated_api_version = None
	dedicated_title = None

	server_is_dedicated = None
	server_is_server = None
	server_ip = None
	server_p2p_port = None
	server_port = None
	server_player_login = None
	server_player_id = None
	server_download_rate = None # TODO: Update on set.
	server_upload_rate = None # TODO: Update on set.
	server_data_dir = None
	server_map_dir = None
	server_skin_dir = None

	game = None  # tm / sm

	def game_from_environment(self, environment):
		if environment in ['Canyon', 'Stadium', 'Valley', 'Lagoon']:
			return 'tm'
		return 'sm'

Game = _Game()
