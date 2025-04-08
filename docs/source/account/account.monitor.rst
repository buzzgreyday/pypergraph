Monitor
=======

.. note::

    In time we might want to create a more flexible caching solution, like the one found in `web3.py <https://github.com/ethereum/web3.py/blob/main/web3/utils/caching.py>`_.

Handles transaction caching and monitors Rx emitted Account events.

.. code-block:: python

    account = DagAccount()
    monitor = Monitor(account=account, state_storage_path="/full/path/state_storage.json")

-----

Caching
^^^^^^^

Transactions
------------

Transactions are added to cache like this:

.. code-block:: python

    account = DagAccount()
    monitor = Monitor(account=account, state_storage_path="/full/path/state_storage.json")
    pending_tx = await account.transfer(secret.to_address, 50000, 200000)
    await monitor.add_to_mem_pool_monitor(pending_tx) # Add transaction to cache and monitor for state changes.

After adding transaction to cache, it will be monitored for state changes until the transaction is confirmed.

Caching relies on ``StateStorageDB`` which is also used to perform keyring storage operations (keyring data is registered with key ``pypergraph-vault``).

Transactions are cached as key ``f"network-{network_info['network_id'].lower()}-mempool"``, with prefix ``"pypergraph-"`` (e.g. mainnet: ``"pypergraph-network-mainnet-mempool"``, etc.)

.. dropdown:: Memory Pool Store Content
   :animate: fade-in

   .. include:: /shared/state_storage.json
      :code: json

-----

Event Observer
^^^^^^^^^^^^^^

Events are emitted and observed using ``RxPy``. There's three ways methods for easily subscribe to ``network_changes``,
``account`` ``login`` and ``logout`` and transaction ``mem_pool`` updates.

-----

Transaction Memory Pool
-----------------------

Transactions state changes are updated in ``DagWalletUpdate``.

**DagWalletUpdate**

+---------------------------+-------------------------------------+---------------------------------------------------------------------+
| **Key**                   | **Type**                            | **Description**                                                     |
+===========================+=====================================+=====================================================================+
| ``pending_has_confirmed`` | ``bool``, ``False (default)``       | If a pending has confirmed.                                         |
+---------------------------+-------------------------------------+---------------------------------------------------------------------+
| ``trans_txs``             | ``List[PendingTransaction]``        | A list of all pending transactions.                                 |
+---------------------------+-------------------------------------+---------------------------------------------------------------------+
| ``tx_changed``            | ``bool``, ``False (default)``       | If any change occurred (e.g. transaction dropped, confirmed, etc.)  |
+---------------------------+-------------------------------------+---------------------------------------------------------------------+

**Subscribe to mem_pool Changes**

.. code-block:: python

    from pypergraph import DagAccount

    account = DagAccount()
    monitor = Monitor(account, state_storage_file_path="state_storage.json")

    def safe_mem_pool_process_event(observable):
        print(f"Transaction Memory Pool: {observable}")
        return of(observable)

    mem_pool_sub = monitor.subscribe_mem_pool(safe_mem_pool_process_event)
    account.connect('integrationnet')
    account.login_with_seed_phrase(secret.mnemo)
    pending_tx = await account.transfer(secret.to_address, 50000, 200000)
    await monitor.add_to_mem_pool_monitor(pending_tx)
    await asyncio.sleep(90)
    account.logout()
    mem_pool_sub.dispose()

The pending transactions will be monitored until confirmed by the network.

-----

Network Changes
---------------


