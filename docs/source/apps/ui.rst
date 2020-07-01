
User Interface
==============

You are free to implement any User Interface features in your app yourself. You can use the template engine Jinja2 for
getting values from the Python code inside of your XML that will be displayed to the client.

On this page you will find out how to implement a simple template and maniascript integration. As well as the useful
manialink classes for hiding or showing for specific view styles.


Using templates
---------------

To use templates, use the :class:`pyplanet.views.template.TemplateView` class (click on the class for the API docs).
You can provide the class property `template_name` which should contain the exact template filename and path.

Example for the example_app:

.. code-block:: python

		class SampleView(TemplateView):
			template_name = 'example_app/test.xml'  # template should be in: ./example_app/templates/test.xml
			# Some prefixes that can be used in the template_name:
			#
			# - core.views: ``pyplanet.views.templates``.
			# - core.pyplanet: ``pyplanet.apps.core.pyplanet.templates``.
			# - core.maniaplanet: ``pyplanet.apps.core.pyplanet.templates``.
			# - core.trackmania: ``pyplanet.apps.core.trackmania.templates``.
			# - core.shootmania: ``pyplanet.apps.core.shootmania.templates``.
			# - [app_label]: ``[app path]/templates``.


Providing data to the template can be done with several overriden methods in the class itself.

**Async Method get_context_data():**
 	Return the global context data here. Make sure you use the super() to retrieve the current context.
**Async Method get_all_player_data(logins):**
 	Retrieve the player specific dictionary. Return dict with player as key and value should contain the data dict.
**Async Method get_per_player_data(login):**
 	Retrieve the player specific dictionary per player. Return dict with the data dict for the specific login (player).

Make sure you visit the class documentation for all the methods on the TemplateView: :class:`pyplanet.views.template.TemplateView`


Global Resources and Variables
``````````````````````````````
New since 0.9.0 are some of the global resources and variables available in the templates at any time.
The following list is available:

- *_instance*: The PyPlanet instance is available with this variable. See :class:`pyplanet.core.instance.Instance` for more information.
- *_game*: The game object is available with some game information. See :class:`pyplanet.core.game._Game` for more information.
- *_app*: The App instance if in any App. Not always available, only inside apps.

With these three global variables/objects you are able to retrieve a lot of information about the current situation on the server
and the versions of the server, title, and such.

Template Content
````````````````

The actual XML you include with the `template_name` property is the file that get's loaded on rendering.
The file can contain anything and can be enriched with the Jinja2 Template Language.

For the Jinja2 documentation we refer to the following page: http://jinja.pocoo.org/docs/2.10/

Example of a XML template with Jinja2 statements:

.. code-block:: xml

  <frame pos="0 -40" id="sample_frame">
    {% if variable == 'value' %}
      <label pos="0 0" size="30 5" text="Variable contains value!" textsize="1.2" valign="top" />
    {% else %}
      <label pos="0 0" size="30 5" text="Variable does not contain value!" textsize="1.2" valign="top" />
    {% endif %}
  </frame>


ManiaScript
-----------

Including ManiaScript to your ManiaLink template is pretty simple actually. Even including global libraries provided by
the PyPlanet team is pretty easy. We will explain how you include ManiaScript in your ManiaLink template.

To include ManiaScript in your ManiaLink template, make sure you create a new file besides your ManiaLink template ending
with `.Script.Txt` and add the following line to your ManiaLink (XML) template:

.. code-block:: xml

  <script><!-- {% include 'my_app/sample.Script.Txt' %} --></script>

That's it! Now you can start with writing ManiaScript in the `sample.Script.Txt`. You can use Jinja2 inside your
ManiaScript to add dynamic content as well.


To include libraries from PyPlanet inside of your ManiaScript, use the following in your `.Script.Txt` file:

.. code-block:: text

  // Includes
  {% include 'core.views/libs/TimeUtils.Script.Txt' %}

.. warning::

  Remember, the core script utils can change behaviour at any time!


TimeUtils Lib
`````````````

The TimeUtils contains several useful utils for working with times.
The full path: ``core.views/libs/TimeUtils.Script.Txt``.

**Text LeftPad(Integer number, Integer pad)**

This method will make sure the number is left-padded with the number of pads given.

**`Text TimeToText(Integer inTime)`**

This method will format time to text to show local or dedi records for example.


ManiaLink
---------

Useful information about ManiaLink changes or additions made by PyPlanet.
ManiaLink docs can be found here: https://doc.maniaplanet.com/manialink
