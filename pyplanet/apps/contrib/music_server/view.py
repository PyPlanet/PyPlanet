from pyplanet.views.generics.list import ManualListView


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
			'sorting': True,
			'searching': True,
			'width': 100,
		},
		{
			'name': 'Artist',
			'index': 'song_artist',
			'sorting': True,
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
		for song in song_list:
			tags = song[1]
			items.append({
				'index': song_list.index(song)+1,
				'song_name': tags.get('title'),
				'song_artist': tags.get('artist'),
			})
		return items
