# TODO


class CheckRegistry:
	def register(self, check=None, *tags, **kwargs):
		pass

	def run_checks(self):
		return []

	def tag_exists(self, tag, include_deployment_checks=False):
		pass

registry = CheckRegistry()
register = registry.register
run_checks = registry.run_checks
tag_exists = registry.tag_exists
