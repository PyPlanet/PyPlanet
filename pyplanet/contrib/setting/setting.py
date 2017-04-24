
class _Setting:
	pass


class CoreSetting(_Setting):
	pass


class AppSetting(_Setting):

	def __init__(
		self, code: str, name: str, description: str = None, app_label: str = None
	):
		self.app_label = app_label
		pass
