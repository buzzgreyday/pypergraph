Keyring Accounts
================

.. admonition:: TODO
   :class: note

   In time I would like to add support for account injection. This will require ``pypergraph.keyrings.registry`` to
   be refactored.

Accounts contain methods for deriving keys, etc. Besides the default ``dag_account`` and ``eth_account`` modules,
the ``accounts`` sub-package also contain the an asset library. This can be used to add additional token support.

**Add a token to the library**

