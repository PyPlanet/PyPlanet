"""
The PIP module contains utilities to upgrade packages in the installation of PyPlanet from the application itself.
"""
import logging
import os
import site
import subprocess
import sys
import tempfile


class Pip:
	def __init__(self):
		self.command = None
		self.virtual_env = None
		self.install_dir = None
		self.pyplanet_dir = None
		self.writable = False
		self.user_flag = False
		self.can_use_user_flag = False

		self.is_supported = False

		self.investigate_environment()

	@classmethod
	def autodetect_pip(cls):
		commands = [[sys.executable, "-m", "pip"],
					[os.path.join(os.path.dirname(sys.executable), "pip.exe" if sys.platform == "win32" else "pip")],

					# this should be our last resort since it might fail thanks to using pip programmatically like
					# that is not officially supported or sanctioned by the pip developers
					[sys.executable, "-c", "import sys; sys.argv = ['pip'] + sys.argv[1:]; import pip; pip.main()"]]

		for command in commands:
			p = subprocess.Popen(command + ['--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			_, _ = p.communicate()
			if p.returncode == 0:
				logging.getLogger(__name__).info("Using \"{}\" as command to invoke pip".format(" ".join(command)))
				return command

		return None

	def investigate_environment(self):
		"""
		This method investigates the environment of the project (checks for virtualenv/pyenv/--user or system wide installation).
		"""
		self.command = Pip.autodetect_pip()
		if not self.command:
			return
		self.pyplanet_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

		# Checking PIP installation and compatibility...
		test_package = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'pip_test_pkg')
		temp_file = tempfile.NamedTemporaryFile()
		data = dict()

		try:
			p = subprocess.Popen(
				self.command + ['install', '.'],
				stdout=subprocess.PIPE, stderr=subprocess.PIPE,
				cwd=test_package,
				env=dict(
					TESTBALLOON_OUTPUT=temp_file.name
				)
			)
			_, _ = p.communicate()

			with open(temp_file.name) as f:
				for line in f:
					key, value = line.split("=", 2)
					data[key] = value
		except Exception as e:
			logging.getLogger(__name__).error("Failed to check if PIP is supported. Failed to investigate PIP installation.")
			logging.getLogger(__name__).exception(e)
			return

		install_dir_str = data.get("PIP_INSTALL_DIR", None)
		virtual_env_str = data.get("PIP_VIRTUAL_ENV", None)
		writable_str = data.get("PIP_WRITABLE", None)

		if install_dir_str is not None and virtual_env_str is not None and writable_str is not None:
			self.install_dir = install_dir_str.strip()
			self.virtual_env = virtual_env_str.strip() == "True"
			self.writable = writable_str.strip() == "True"

			self.can_use_user_flag = not self.virtual_env and site.ENABLE_USER_SITE

			self.is_supported = self.writable or self.can_use_user_flag
			self.user_flag = not self.writable and self.can_use_user_flag

			logging.getLogger(__name__).info(
				"pip installs to {} (writable -> {}), --user flag needed -> {}, virtual env -> {}".format(
					self.install_dir,
					"yes" if self.writable else "no",
					"yes" if self.user_flag else "no",
					"yes" if self.virtual_env else "no"
				)
			)
			logging.getLogger(__name__).info("==> pip ok -> {}".format("yes" if self.is_supported else "NO!"))
		else:
			logging.getLogger(__name__).error(
				"Could not detect desired output from pip_test_pkg install, got this instead: {!r}".format(data)
			)

	def install(self, package, target_version=None):
		"""
		Install (or upgrade) package to target version given or to latest if no target version given.

		:param package: Package name
		:param target_version: Target version
		:return: Return code from PIP, stdout and stderr
		"""
		if not self.is_supported:
			raise Exception('Pip environment is not supported!')

		command = self.command + ['install']
		if self.user_flag:
			command += ['--user']
		command += ['-U', '{}{}'.format(
			package, '=={}'.format(target_version) if target_version else ''
		)]

		p = subprocess.Popen(
			command,
			stdout=subprocess.PIPE, stderr=subprocess.PIPE,
			cwd=self.pyplanet_dir,
		)
		stdout, stderr = p.communicate()

		return p.returncode, stdout, stderr
