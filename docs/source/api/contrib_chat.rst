
pyplanet.contrib.chat
=====================

Sending chat messages
---------------------

We implemented an abstraction that will provide auto multicall and auto prefixing for you. You can use the following
statements for example:

.. code-block:: python

  # Send chat message to all players.
  await self.instance.chat('Test')

  # Send chat message to specific player or multiple players.
  await self.instance.chat('Test', 'player_login')  # Sends to single player.
  await self.instance.chat('Test', 'player_login', player_instance)  # Sends to both players.

  # Execute in chain (Multicall).
  await self.instance.chat.execute(
    'global_message',
    self.instance.chat('Test', 'player_login'),
    self.instance.chat('Test2', 'player_login2'),
  )

  # You can combine this with other calls in a GBX multicall:
  await self.instance.gbx.multicall(
    self.instance.gbx.prepare('SetServerName', 'Test'),
    self.instance.chat('Test2', 'player_login2'),
  )


API Documentation
-----------------

.. automodule:: pyplanet.contrib.chat
  :members:
