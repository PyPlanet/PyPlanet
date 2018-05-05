from pyplanet.views.generics.list import ManualListView


class MusicListView(ManualListView):
	title = 'Songs'
	icon_style = 'Icons128*128_1'
	icon_substyle = 'Statistics'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.provide_search = True

	async def get_fields(self):
		return [
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
				'sorting': True,
				'searching': True,
				'width': 100,
				'action': self.action_playlist
			},
			{
				'name': 'Artist',
				'index': 'song_artist',
				'sorting': True,
				'searching': True,
				'width': 100,
			},
		]

	async def get_data(self):
		items = []
		song_list = self.app.songs
		for song in song_list:
			tags = song[1]
			items.append({
				'index': song_list.index(song) + 1,
				'song_name': tags.get('title', '-unknown title-'),
				'song_artist': tags.get('artist', '-unknown artist-'),
			})
		return items

	async def action_playlist(self, player, values, song_info, *args, **kwargs):
		await self.app.add_to_playlist(player, song_info['index']-1)


class PlaylistView(ManualListView):
	title = 'Playlist'

	def __init__(self, app):
		super().__init__(self)
		self.app = app
		self.manager = app.context.ui
		self.provide_search = True#

	async def get_fields(self):
		return [
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
				'sorting': True,
				'searching': True,
				'width': 100,
				'action': self.action_drop
			},
			{
				'name': 'Artist',
				'index': 'song_artist',
				'sorting': True,
				'searching': True,
				'width': 50,
			},
			{
				'name': 'Requested by',
				'index': 'juke_player',
				'sorting': True,
				'searching': True,
				'width': 60
			}
		]

	async def action_drop(self, player, values, song_info, **kwargs):
		await self.app.drop_from_playlist(player, song_info)

	async def get_data(self):
		items = []
		playlist = self.app.playlist
		for song in playlist:
			tags = song['song'][1]
			items.append({
				'index': playlist.index(song) + 1,
				'song_name': tags.get('title'),
				'song_artist': tags.get('artist'),
				'juke_player': song['player']
			})
		return items
