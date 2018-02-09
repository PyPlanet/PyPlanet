from pyplanet.views.generics.list import ManualListView
from tinytag import TinyTag


class MusicListView(ManualListView):
	title = 'Songs'
	icon_style = 'Icons128*128_1'
	icon_substyle = 'Statistics'

	fields = [
		{
			'name': '#',
			'index': 'index',
			'sorting': True,
			'searching': False,
			'width': 10,
			'type': 'label'
		},
		{
			'name': 'Song',
			'index': 'song_name',
			'sorting': False,
			'searching': True,
			'width': 100,
		},
		{
			'name': 'Artist',
			'index': 'song_artist',
			'sorting': False,
			'searching': True,
			'width': 100,
		},
	]

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.provide_search = True

	async def get_data(self):
		items = []
		song_list = self.app.songs
		server_url = self.app.server
		for idx, song in enumerate(song_list):
			items.append({
				'index': idx,
				'song_name': song.replace(server_url, "").split("-")[1],
				'song_artist': song.replace(server_url, "").split("-")[0]
			})
		return items
