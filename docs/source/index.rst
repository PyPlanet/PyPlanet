Welcome to PyPlanet's documentation!
====================================

..  image:: /_static/logo/pyplanet-sm.png
    :scale: 50%
    :align: right

PyPlanet is a Maniaplanet Dedicated Server Controller that works on Python 3.5 and later.
Because Maniaplanet is using an system that can be event based we use AsyncIO to provide
a event loop and have simultaneously processing of received events from the dedicated server.

The code is open source, and `available on GitHub`_.

.. _available on GitHub: https://github.com/PyPlanet

The main documentation for the site is organized into a couple sections:

* :ref:`user-docs`
* :ref:`app-docs`
* :ref:`about-docs`

Information about development of apps and the core is also available under:

* :ref:`dev-docs`


..  _user-docs:

..  toctree::
    :maxdepth: 2
    :caption: User Documentation

    intro/index
    convert/index


.. _app-docs:

..  toctree::
    :maxdepth: 2
    :glob:
    :caption: Apps Documentation

    apps/contrib/admin
    apps/contrib/jukebox
    apps/contrib/karma
    apps/contrib/local_records
    apps/contrib/players


.. _dev-docs:

..  toctree::
    :maxdepth: 2
    :caption: Developer Documentation

    core/index
    apps/index

    api/index


.. _about-docs:

..  toctree::
    :maxdepth: 1
    :caption: About PyPlanet

    support
    privacy
    changelog
    todo


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Links
=====

| Documentation: http://pypla.net/
| GitHub: https://github.com/PyPlanet
| PyPi:
