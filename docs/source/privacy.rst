
Privacy
=======


Error reports
-------------

We have an automated error reporting system in place that tells the developers or PyPlanet when there are instabilities in
the core code or in one of the contributed and bundled apps.

**What are we catching and reporting**

We will catch so called uncaught exceptions, these are mostly not handled by one of the functions inside of the code.
When it's not handled, the whole function or call to that function is halt and stopped. When this happends, we send
an report with the full traceback (all the touched lines of code in order) with the data of the exception.

We also have some specific messages we forward towards the error reporting service. For this kind of messages it's really
important we get to know them. For example a memory leak in one of the apps or contributed apps. Or a captured exception
but it's not known or handled right.

**What data are we sending with the report**

Depending on the setting we send minimum of full data about your installation and server. By default you will contribute
with the full data option.

Full (level 2 or 3):

* Server dedicated login, paths to maps, scripts, modes, all kind of dedicated configuration.
* Variable data in local method, inside of the exception call.
* Exception with trace or error message including module and line.
* Share information (filtered to only the basic information, *no user specific data!!*) to app developers (must be level 3)

Minimum (level 1):

* Exception with basic trace or error message.

**Where will the data be stored**

All the data will be stored in an analyse and reporting tool that is fully self hosted by Toffe. We protect the installation
with HTTPS and don't allow unauthorized or non-pyplanet team members to access the data.

**What about sensitive information**

We will replace any sensitive information that seems to be either a key, serial or password by asterisk. This is done in
the reporting process.

**How to change the behaviour of reporting**

You can add this line to your `base.py` file to change the behaviour.

.. code-block:: python

  # Error reporting
  # See documentation for the options, (docs => privacy).
  # Options:
  # 0 = Don't report any errors or messages.
  # 1 = Report errors with only traces.
  # 2 = Report errors with traces and server data.
  # 3 = Report errors with traces and server data, provide data to contributed apps (only pyplanet team has access).
  LOGGING_REPORTING = 3

.. warning::

  **We really like to improve the stability of PyPlanet**, therefor we kindly ask you to keep the setting on, or at least
  at level ``2``.


Analytics & Telemetry
---------------------

For future improvements and look into the usage of PyPlanet and it's apps we collect the following information:

- PyPlanet version
- Python version
- Server version
- Operating system
- Server login
- Server titlepack
- Active apps
- Total number of players

We do this by sending so called ping-updates every hour with up-to-date status about the server. By collecting this
we gain information on how to improve with targeting specific titles or apps for updates. And to improve the operating system
support if required.

You can turn this off by adding this line to your ``settings/base.py``:

.. code-block:: python

  ANALYTICS = False
