
Dedicated/Script methods
========================

From your app you can execute dedicated GBX methods (or scripted methods) with the following methods:

.. code-block:: python

  # Force player_login into spectator.
  await self.instance.gbx('ForceSpectator', 'player_login', 1)

  # Execute multiple gbx actions in a multicall (Is way faster).
  await self.instance.gbx.multicall(
    self.instance.gbx('Method', 'arg1', 'arg2'),
    self.instance.gbx('Method', 'arg1', 'arg2'),
    self.instance.gbx('Method', 'arg1', 'arg2'),
  )
