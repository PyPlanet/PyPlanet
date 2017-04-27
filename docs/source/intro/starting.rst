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

You always have to be in the projects virtualenv if you have enabled this during the installation.

**virtualenv**:

.. code-block:: bash

  # Linux / Mac OS
  source env/bin/activate

  # Windows
  env\Scripts\Activate.bat


**pyenv**:

.. code-block:: bash

  pyenv activate my-virtual-env


Start PyPlanet
~~~~~~~~~~~~~~

Head to your projects folder where the file ``manage.py`` is located in your terminal and execute the following command:

.. code-block:: bash

  ./manage.py start

This will start your PyPlanet setup.
