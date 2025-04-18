Monitor
=======

.. note::
    In the future, we aim to create a more flexible caching solution, similar to the one found in web3.py <https://github.com/ethereum/web3.py/blob/main/web3/utils/caching.py>_.

The Monitor class handles transaction caching and observes events emitted by Account instances.

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

After adding a transaction to the cache, it will be monitored for state changes until the transaction is confirmed.
The caching mechanism relies on the ``StateStorageDB``, which is also used for keyring storage operations (keyring data is registered with the key pypergraph-vault).
Transactions are cached with the key format ``"pypergraph-network-{network_id}-mempool"`` (e.g., ``"pypergraph-network-mainnet-mempool"`` for mainnet).

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

**Subscribe to mem_pool Updates**

.. code-block:: python

    from pypergraph import DagAccount

    account = DagAccount()
    monitor = Monitor(account, state_storage_file_path="state_storage.json")

    def safe_mem_pool_process_event(observable):
        print(f"Monitor :: Transaction Memory Pool: {observable}")
        return of(observable)

    mem_pool_sub = monitor.subscribe_mem_pool(safe_mem_pool_process_event)
    account.connect('integrationnet')
    account.login_with_seed_phrase(secret.mnemo)
    pending_tx = await account.transfer(secret.to_address, 50000, 200000)
    await monitor.add_to_mem_pool_monitor(pending_tx)
    await asyncio.sleep(90)
    account.logout()
    mem_pool_sub.dispose()

The pending transactions will be monitored until all is confirmed by the network.

-----

Network Changes
---------------

The ``DagTokenNetwork`` has a class variable ``_network_change`` ``BehaviorSubject`` that emits updates with the following structure:

**Observable Event**

+------------------------------------+------------------------------------------+--------------------------------------+
| **Key**                            | **Value**                                | **Description**                      |
+====================================+==========================================+======================================+
| ``"module"``                       | ``"network"``                            | ID of the emitting Python module.    |
+------------------------------------+------------------------------------------+--------------------------------------+
| ``"type"``                         | ``"network_change"``                     | The type of event emitted by the     |
|                                    |                                          | module.                              |
+------------------------------------+------------------------------------------+--------------------------------------+
| ``"event"``                        | ``{"network_id": "integrationnet", ...}``| New network settings.                |
+------------------------------------+------------------------------------------+--------------------------------------+

**Subscribe to Network Changes**

.. code-block:: python

    from pypergraph import DagAccount

    account = DagAccount()
    monitor = Monitor(account, state_storage_file_path="state_storage.json")

    def safe_network_process_event(observable: dict):
        # Simulate event processing (replace with your logic)
        print(f"Monitor :: Injected callable network event subscription: {observable}")
        return of(observable)  # Emit the event downstream

    network_sub = monitor.subscribe_network(safe_network_process_event)
    account.connect('integrationnet')
    network_sub.dispose()
    asyncio.sleep(1)

-----

Account Events
--------------

**Observable Event**

+------------------------------------+------------------------------------------+--------------------------------------+
| **Key**                            | **Value**                                | **Description**                      |
+====================================+==========================================+======================================+
| ``"module"``                       | ``"account"``                            | ID of the emitting Python module.    |
+------------------------------------+------------------------------------------+--------------------------------------+
| ``"event"``                        | ``"login"`` or ``"logout"``              |                                      |
+------------------------------------+------------------------------------------+--------------------------------------+

**Subscribe to Account Events**

.. code-block:: python

    from pypergraph import DagAccount, Monitor

    account = DagAccount()
    monitor = Monitor(account, state_storage_file_path="state_storage.json")

    def safe_account_process_event(observable):
        if observable["event"] == "logout":
            print("Monitor :: Injected callable account event: logout signal received.")
        elif observable["event"] == "login":
            print("Monitor :: Injected callable account event: login signal received.")
        else:
            print(f"Monitor :: Unknown signal received by injected callable account event: {observable}")
        return of(observable)

    account_sub = monitor.subscribe_account(safe_account_process_event)
    account.login_with_seed_phrase(secret.mnemo)
    await asyncio.sleep(1) # Wait a bit for update
    account.logout()
    await asyncio.sleep(1)
    account_sub.dispose()

-----

Get Pending and Confirmed Transactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Monitor class provides methods to retrieve pending and confirmed transactions from the cache and the block explorer.

.. code-block:: python

    from pypergraph import DagAccount, Monitor

    account = DagAccount()
    account.login_with_seed_phrase(secret.mnemo)
    monitor = Monitor(account, state_storage_file_path="state_storage.json")
    lst = await monitor.get_latest_transactions(address=account.address, limit=10, search_after=None)
