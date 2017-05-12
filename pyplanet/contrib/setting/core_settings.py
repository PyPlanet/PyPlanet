from pyplanet.contrib.setting import Setting

# Performance mode setting
performance_mode = Setting(
	'performance_mode', 'Performance mode playercount', Setting.CAT_BEHAVIOUR, type=int,
	description='Above this amount of players the performance mode will be enabled.',
	default=30
)
