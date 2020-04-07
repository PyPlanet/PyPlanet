
from pyplanet.core.checks import Error


class CheckRegistry:
	def __init__(self):
		self.registered_checks = set()
		self.deployment_checks = set()

	def register(self, check=None, **kwargs):
		def inner(check):
			checks = self.deployment_checks if kwargs.get('deploy') else self.registered_checks
			checks.add(check)
			return check

		if callable(check):
			return inner(check)
		return inner

	def run_checks(self, app_configs=None, tags=None, include_deployment_checks=False, instance=None):
		errors = list()
		checks = self.get_checks(include_deployment_checks)

		try:
			from pyplanet.conf import settings
			_ = settings.DEBUG
		except:
			errors.append(
				Error(
					'Settings module not found, make sure you set PYPLANET_SETTINGS or the Cli option --settings!'
				)
			)

		for check in checks:
			new_errors = check(app_configs=app_configs, instance=instance)
			try:
				new_errors_iter = iter(new_errors)
			except TypeError:
				raise Exception(
					'The function {} did not return a list. All functions registered with the checks registry must return a list.'.format(check)
				)

			errors.extend(new_errors)

		return errors

	def tag_exists(self, tag, include_deployment_checks=False):
		# TODO: Extend the check registry class.
		return False

	def get_checks(self, include_deployment_checks=False):
		checks = list(self.registered_checks)
		if include_deployment_checks:
			checks.extend(self.deployment_checks)
		return checks


registry = CheckRegistry()
register = registry.register
run_checks = registry.run_checks
tag_exists = registry.tag_exists
