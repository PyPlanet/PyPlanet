|
|
|
|
|
|

Starting PyPlanet
-----------------

After following the instructions on how to `install <installation>`__ and `configure <configuration>`__ PyPlanet you are
ready to start up the controller itself.


Activate virtualenv
~~~~~~~~~~~~~~~~~~~

You always have to be in the projects virtualenv!

**virtualenv**:

.. code-block:: bash

  # Linux / Mac OS
  source env/bin/activate

  # Windows
  env\Scripts\Activate.bat


**PyEnv**:

.. code-block:: bash

  pyenv activate pyplanet
  # pyplanet is your virtualenv name here!


Start PyPlanet
~~~~~~~~~~~~~~

Head to your projects folder where the file ``manage.py`` is located in your terminal and execute the following command:

.. code-block:: bash

  ./manage.py start

This will start your PyPlanet setup.
