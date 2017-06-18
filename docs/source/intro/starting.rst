
Starting PyPlanet
=================

.. contents::
  :depth: 2

After following the instructions on how to `install </intro/index>`__ and `configure </intro/configuration>`__ PyPlanet you are
ready to start up the controller itself.

By default, PyPlanet will always run in the foreground. That's why we have several steps to make PyPlanet run in the background
and as a service on your server. As a side-note we also have the screen method described. It's a matter of preference and support.

.. hint::

  If you use an virtual environment, make sure it's activated. We will not show this in some instructions, but always
  activate before starting PyPlanet.


Start/stop with Screen (Linux)
------------------------------

**Screen is a feature on Linux distributions that makes it possible to start a virtual terminal window, and keep the terminal**
**open in the background for as long as required. You can watch or control the screen from multiple SSH sessions, making it ideal**
**for platforms that require multiuser access to the servers while not require the root privileges required for the services.**

1. Installation of screen
~~~~~~~~~~~~~~~~~~~~~~~~~

To use Screen for PyPlanet you have to install it for your OS.

**Debian / Ubuntu:**:

``sudo apt-get install screen``

**Fedora / RHEL**:

``sudo yum install screen``

2. Start a new screen
~~~~~~~~~~~~~~~~~~~~~

You can start a new screen session with this command. Remember that you only have to do this once for starting a new session.
After executing this command you will create and directly attach to this screen instance.

.. code-block:: bash

  screen -S name-of-screen


3. Open a screen
~~~~~~~~~~~~~~~~

If you have followed step 2, please skip this step, this step is meant for so called 'reattaching' to the screen.

To list the screens on this user account use: ``screen -ls``.

To reattach to a deattached screen, use: ``screen -r name-of-screen``.
If you can't attach, you might have another session attached or need to use the numeric screen id's from the list command.

To reattach to an already attached screen, use: ``screen -x name-of-screen``.
Again, if this fails, try the numeric id from the list command.

From now you are in the virtual terminal session, when you accidentally disconnect your SSH tunnel, the process inside the screen will still
be active!

4. Start PyPlanet
~~~~~~~~~~~~~~~~~

Make sure you activated your virtual environment first.

Head to your projects folder where the file ``manage.py`` is located in your terminal and execute the following command:

.. code-block:: bash

  ./manage.py start

This will start your PyPlanet project environment(s).

5. Leaving the screen
~~~~~~~~~~~~~~~~~~~~~

To leave the screen the right way (deattach) you have to do the following keyboard combination:

:kbd:`CTRL+A` then release, and press :kbd:`D`.

If you want to exit and **destroy** the screen, just cancel all programs inside, and type ``logout`` or use :kbd:`CTRL+D`.



Install SystemD Service (Linux)
-------------------------------

**SystemD is a pretty new init system that is included in the newest distributions.**
**For example, Ubuntu 16.04 and higher, Debian 8 and higher make use of SystemD.**
**SystemD will replace the old sysvinit system and make it easy to start/stop and automatically restart services (including during the OS boot)**

.. warning::

  This method is slightly harder, and require you to have root rights al the time (even to (re)start).

  **This also requires you to use PyEnv.**


1. Installing the service
~~~~~~~~~~~~~~~~~~~~~~~~~

Head towards your systemd configuration folder by executing the following command(s):

**Debian / Ubuntu / Fedora / RHEL / Most other Linux distros:**:

``cd /etc/systemd/system``


2. Determinate paths
~~~~~~~~~~~~~~~~~~~~

First of all, we have to know the following paths:

1. Full path to the PyPlanet executable.
2. Full path to the project root.
3. The user and group you want to run PyPlanet under.
4. Your service name. (in our examples ``pyplanet.service`` and ``pyplanet``)

2.1. Full PyPlanet path
```````````````````````

You can check the full path to the pyplanet cli interface by executing this: ``whereis pyplanet``.
The outcome is the path, in our example it's ``/home/toffe/.pyenv/shims/pyplanet``.


2.2. Full project path
``````````````````````

Where is the root of the PyPlanet project located, this is the folder where the ``settings`` folder and the ``manage.py`` file exist.
In our example it's ``/path/to/your/pyplanet/project``.


2.3. Running user and group
```````````````````````````

It's important to not run as root! That's why you want to use a secondary user on your system.

Find out the current user and group name with the following command: ``echo id`` (don't execute with sudo!).

This will output something like this:

.. code-block:: bash

  uid=1000(toffe) gid=1000(toffe) groups=1000(toffe),4(adm),24(cdrom),27(sudo),30(dip),46(plugdev),113(lpadmin),128(sambashare),133(wireshark),140(kvm),141(libvirtd),998(bumblebee),999(docker)

We only need two items in there, and its the value inside of the brackets of the first item (`uid=x`), in our case ``toffe`` which is the user.

And the second value is the group, just after the `gid=x`, and inside the brackets, in our case also ``toffe``.


3. Create the service definition file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After going to the right location you have to create a new file called ``pyplanet.service``. You can rename it as you want!

.. code-block:: bash

  sudo nano pyplanet.service
  # Or use your os editor, like vim or pico. Make sure you are still in the folder from step 1!

After opening the editor, paste the contents bellow and change the contents according the steps above.

.. code-block:: bash

  [Unit]
  After=syslog.target network.target

  [Service]
  WorkingDirectory=/path/to/your/pyplanet/project
  Environment="PYTHONPATH=/path/to/your/pyplanet/project"
  ExecStart=/home/toffe/.pyenv/shims/pyplanet start --settings=settings
  SyslogIdentifier=pyplanet

  Restart=always
  StandardOutput=syslog
  StandardError=syslog
  User=toffe
  Group=toffe

  [Install]
  WantedBy=multi-user.target

After changing the contents, save the file and continue to the next step.


4. Reload systemd
~~~~~~~~~~~~~~~~~

After installing the new service file you have to let systemd know that you changed something. Do this with the following command:

.. code-block:: bash

  sudo systemctl daemon-reload


5. Starting/stopping PyPlanet
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

From now you can start, stop and restart your controller with the following commands: (the pyplanet name is your service file name).

.. code-block:: bash

  systemctl start pyplanet
  systemctl stop pyplanet
  systemctl restart pyplanet

To view the logs of the PyPlanet instance, type one of this commands:

.. code-block:: bash

  journalctl --unit pyplanet.service -xe
  journalctl --unit pyplanet.service -f


6. Starting at boot
~~~~~~~~~~~~~~~~~~~

Activate the service to have it started when your machine starts.

.. code-block:: bash

  systemctl enable pyplanet


Start standalone and in foreground (Linux and Windows)
------------------------------------------------------

1. Go to your project folder
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you change directory to your project root (contains the ``manage.py`` file).

.. code-block:: bash

  cd /my/project/location


2. Activate virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure you activated your virtual environment.


.. code-block:: bash

  # Linux / Mac OS
  pyenv activate pyplanet

  # Windows
  env\Scripts\activate.bat


.. tip::

  Don't know how to setup the environment exactly? Head to :doc:`Windows </intro/installation-windows>` or :doc:`Linux </intro/installation-linux>` guides.


3. Start PyPlanet
~~~~~~~~~~~~~~~~~

.. code-block:: bash

  # Linux:
  ./manage.py start

  # Windows
  manage.py start

This will start your PyPlanet setup.
