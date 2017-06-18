import stat
import os
import shutil
import sys
import pyplanet

from os import path
from jinja2 import Environment

from pyplanet.conf import settings
from pyplanet.core.management import BaseCommand, CommandError


class TemplateCommand(BaseCommand):
	"""
	Template command is an abstract command to copy template files anywhere.
	"""
	requires_system_checks = False
	requires_migrations_checks = False
	leave_locale_alone = True

	# Define your template files (files that should be templated) here.
	template_files = []

	# Set the template base dir.
	template_base_dir = path.join(pyplanet.__path__[0], 'conf')

	def add_arguments(self, parser):
		parser.add_argument('name', help='Name of folder/app to create.')
		parser.add_argument('directory', nargs='?', help='Optional destination directory. Defaults to new directory.')

	def handle(self, app_or_project, name, target=None, **options):
		self.app_or_project = app_or_project
		self.paths_to_remove = []
		self.verbosity = options['verbosity']

		self.validate_name(name, app_or_project)

		# If it's a relative to the current dir, replace it.
		if name == '.':
			name = ''

		# if some directory is given, make sure it's nicely expanded
		if target is None:
			top_dir = path.join(os.getcwd(), name)
			try:
				os.makedirs(top_dir)
			except FileExistsError:
				listdir = os.listdir(top_dir)
				if len(listdir) == 0 or (len(listdir) == 1 and 'env' in listdir):
					pass
				else:
					raise CommandError("'%s' already exists" % top_dir)
			except OSError as e:
				raise CommandError(e)
		else:
			top_dir = os.path.abspath(path.expanduser(target))
			if not os.path.exists(top_dir):
				raise CommandError("Destination directory '%s' does not "
								   "exist, please create it first." % top_dir)

		if self.verbosity >= 2:
			self.stdout.write("Rendering {} template files\n".format(app_or_project))

		base_name = '{}_name'.format(app_or_project)
		base_subdir = '{}_template'.format(app_or_project)
		base_directory = '{}_directory'.format(app_or_project)
		camel_case_name = 'camel_case_{}_name'.format(app_or_project)
		camel_case_value = ''.join(x for x in name.title() if x != '_')

		context = dict(options, **{
			base_name: name,
			base_directory: top_dir,
			camel_case_name: camel_case_value,
			'pyplanet_version': pyplanet.__version__,
		})

		# Setup a stub settings environment for template rendering
		try:
			if not settings.configured:
				_ = settings.APPS
		except:
			pass

		template_dir = self.handle_template(base_subdir)
		prefix_length = len(template_dir) + 1
		env = Environment(autoescape=False)

		for root, dirs, files in os.walk(template_dir):
			path_rest = root[prefix_length:]
			relative_dir = path_rest.replace(base_name, name)
			if relative_dir:
				target_dir = path.join(top_dir, relative_dir)
				if not path.exists(target_dir):
					os.mkdir(target_dir)

			for dirname in dirs[:]:
				if dirname.startswith('.') or dirname == '__pycache__':
					dirs.remove(dirname)

			for filename in files:
				if filename.endswith(('.pyo', '.pyc', '.py.class')):
					# Ignore some files as they cause various breakages.
					continue
				old_path = path.join(root, filename)
				new_path = path.join(top_dir, relative_dir, filename.replace(base_name, name))

				if path.exists(new_path):
					raise CommandError("%s already exists, overlaying a "
									   "project or app into an existing "
									   "directory won't replace conflicting "
									   "files" % new_path)

				# Only render the Python files, as we don't want to
				# accidentally render PyPlanet templates files
				if path.join(relative_dir, filename) in self.template_files:
					with open(old_path, 'r', encoding='utf-8') as template_file:
						content = template_file.read()
					template = env.from_string(content)
					content = template.render(context)
					with open(new_path, 'w', encoding='utf-8') as new_file:
						new_file.write(content)
				else:
					shutil.copyfile(old_path, new_path)

				if self.verbosity >= 2:
					self.stdout.write("Creating %s\n" % new_path)
				try:
					shutil.copymode(old_path, new_path)
					self.make_writeable(new_path)
				except OSError:
					self.stderr.write(
						"Notice: Couldn't set permission bits on %s. You're "
						"probably using an uncommon filesystem setup. No "
						"problem." % new_path, self.style.NOTICE)

		if self.paths_to_remove:
			if self.verbosity >= 2:
				self.stdout.write("Cleaning up temporary files.\n")
			for path_to_remove in self.paths_to_remove:
				if path.isfile(path_to_remove):
					os.remove(path_to_remove)
				else:
					shutil.rmtree(path_to_remove)

	def validate_name(self, name, app_or_project):
		if name is None:
			raise CommandError("you must provide %s %s name" % (
				"an" if app_or_project == "app" else "a", app_or_project))
		if app_or_project == 'project' and name == '.':
			return True
		# If it's not a valid directory name.
		if not name.isidentifier():
			raise CommandError(
				"%r is not a valid %s name. Please make sure the name is "
				"a valid identifier." % (name, app_or_project)
			)

	def handle_template(self, subdir):
		return path.join(self.template_base_dir, subdir)

	def make_writeable(self, filename):
		"""
		Make sure that the file is writeable.
		Useful if our source is read-only.
		"""
		if sys.platform.startswith('java'):
			# On Jython there is no os.access()
			return
		if not os.access(filename, os.W_OK):
			st = os.stat(filename)
			new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
			os.chmod(filename, new_permissions)
