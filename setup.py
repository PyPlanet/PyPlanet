import os
import re
from setuptools import setup, find_packages


def long_description():
	try:
		return open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
	except IOError:
		return None


def read_version():
	with open(os.path.join(os.path.dirname(__file__), 'pyplanet', '__init__.py')) as handler:
		return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", handler.read(), re.M).group(1)


def read_requirements(filename):
	with open(os.path.join(os.path.dirname(__file__), filename), 'r') as handler:
		return [line for line in handler.readlines() if not line.startswith('-') and not len(line)]


PKG = 'pyplanet'
######
setup(
	name=PKG,
	version=read_version(),
	description='Maniaplanet Server Controller',
	long_description=long_description(),
	keywords='maniaplanet, controller, plugins',
	license='GNU General Public License v3 (GPLv3)',
	packages=find_packages(),
	package_data={
		'pyplanet/tests': ['pyplanet/tests/**.txt', 'pyplanet/tests/**.json', 'pyplanet/tests/**.xml', 'pyplanet/tests/**.j2']
	},
	install_requires=read_requirements('requirements.txt'),
	tests_require=read_requirements('requirements-dev.txt'),
	extras_require={},
	test_suite='nose.collector',
	include_package_data=True,

	author='Tom Valk',
	author_email='tomvalk@lt-box.info',
	url='https://github.com/tomvlk/PyPlanet-core',

	classifiers=[
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Development Status :: 1 - Planning',

		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3 :: Only',

		'Topic :: Internet',
		'Topic :: Software Development',
		'Topic :: Games/Entertainment',

		'Intended Audience :: System Administrators',
		'Intended Audience :: Developers',

	],
	zip_safe=False,
)
