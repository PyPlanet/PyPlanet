

class Zone:
	def __init__(self, path, continent, country=None, province=None):
		self.path = path
		self.continent = continent
		self.country = country
		self.province = province


def parse_path(path: str) -> Zone:
	parts = path.split('|')

	continent = None
	country = None
	province = None

	if len(parts) > 1:
		continent = parts[1]
	if len(parts) > 2:
		country = parts[2]
	if len(parts) > 3:
		province = parts[3]

	return Zone(path, continent, country, province)
