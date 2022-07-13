PyPlanet
========

.. image:: https://travis-ci.com/PyPlanet/PyPlanet.svg?branch=master
  :target: https://travis-ci.com/PyPlanet/PyPlanet
.. image:: https://ci.appveyor.com/api/projects/status/glsug2u5crt2o66m/branch/master?svg=true
  :target: https://ci.appveyor.com/project/tomvlk/pyplanet
.. image:: https://coveralls.io/repos/github/PyPlanet/PyPlanet/badge.svg?branch=master
  :target: https://coveralls.io/github/PyPlanet/PyPlanet?branch=master
.. image:: https://readthedocs.org/projects/pyplanet/badge/?version=stable
  :target: http://pyplanet.readthedocs.io/en/stable/?badge=stable
  :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/pyplanet.svg
  :target: http://pypi.org/pypi/pyplanet
.. image:: https://img.shields.io/docker/v/pyplanet/pyplanet?label=docker&sort=semver
  :target: https://hub.docker.com/r/pyplanet/pyplanet

.. image:: https://img.shields.io/badge/patreon-donate-yellow.svg
  :target: https://patreon.com/pyplanet
.. image:: https://img.shields.io/badge/paypal-donate-yellow.svg
  :target: https://paypal.me/tomvlk

This repo contains the PyPlanet package.

**For installation, configuration and development instructions head towards our website:**
http://pypla.net/

Git Structure
-------------

Master is always the latest development environment. We develop features in different branches ``feature/*`` or ``bugfix/*`` appending
with the issue key of GitHub.

Crafting releases is done at the ``release/1.1.x`` branches. The branch is created from the master at the moment the freeze moment goes in.
Only bug fixes are accepted to be merged into the release/* or master branches (and merged into release again), name these branches ``bugfix/ISSUE-ID``.

After releasing (from the release branch) it gets a version tag. From this point there is no way back, new bug releases will be crafted
from the release branch (``release/0.1.x`` for example).

Visualization of our current release schedule can be found here: `Release Schedule <https://github.com/PyPlanet/PyPlanet/projects/3>`_

Versioning
----------

All PyPlanet versions bellow 1.0.0 are not using semantic versioning.
After 1.0.0, there is a strict semantic versioning (v2) versioning policy in use.

Contributions
-------------

Pull requests and issues are more then welcome.
Please open a ticket before a pull request if you are not yet sure how to solve or want opinions before your implementation. (optional).
