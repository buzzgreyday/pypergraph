Monitor
=======

.. note::

    In time we might want to create a more flexible caching solution, like the one found in `web3.py <https://github.com/ethereum/web3.py/blob/main/web3/utils/caching.py>)`_.

Handles transaction caching and monitors Rx emitted Account events.

.. code-block:: python

    account = DagAccount()
    monitor = Monitor(account=account, state_storage_path="/full/path/state_storage.json")

This will observe for ``network_change``, ``login`` and ``logout`` events emitted by the ``account``.

-----

Add Transaction to Cache and Monitor for State Change
-----------------------------------------------------


