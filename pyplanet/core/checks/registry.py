from pyplanet.core.checks import Error


class CheckRegistry:
	def register(self, check=None, *tags, **kwargs):
		pass

	def run_checks(self, app_configs=None, tags=None, include_deployment_checks=False):
		errors = list()

		try:
			from pyplanet.conf import settings
			_ = settings.DEBUG
		except:
			errors.append(
				Error(
					'Settings module not found, make sure you set PYPLANET_SETTINGS or the Cli option --settings!'
				)
			)

		# TODO: Extend.

		return errors

	def tag_exists(self, tag, include_deployment_checks=False):
		pass

registry = CheckRegistry()
register = registry.register
run_checks = registry.run_checks
tag_exists = registry.tag_exists
