Account Transactions
====================

Single $DAG Transaction
^^^^^^^^^^^^^^^^^^^^^^^
.. note::
    :code:`Amount` and :code:`fee` are 8 decimal integers (dDAG), i.e. 1 DAG is equal to 100000000 dDAG

.. code-block:: python

    from pypergraph.dag_account import DagAccount
    import asyncio

    async def execute_transfer():
        account = DagAccount()
        account.login_with_seed_phrase("abandon abandon ...")

        transaction_hash = await account.transfer(
            to_address="DAG1...",
            amount=100000000,  # 1 DAG = 10^8 units
            fee=200000
        )
        print(f"Transaction ID: {transaction_hash}")

    asyncio.run(execute_transfer())

.. dropdown:: Transaction Creation Lifecycle
    :animate: fade-in

    .. code-block:: python

        # Transaction preparation
        tx, tx_hash = await account.generate_signed_transaction(
            to_address="DAG1...",
            amount=100000000,
            fee=20000,
            last_ref=await account.network.get_address_last_accepted_transaction_ref(account.address)
        )

        # Network submission
        await account.network.post_transaction(tx)


Batch $DAG Transactions
^^^^^^^^^^^^^^^^^^^^^^^
.. note::
    :code:`Amount` and :code:`fee` are 8 decimal integers (dDAG), i.e. 1 DAG is equal to 100000000 dDAG

.. code-block:: python

    async def batch_transfers():
        account = DagAccount().login_with_seed_phrase("abandon abandon ...")
        transfers = [
            {"to_address": "DAG1...", "amount": 100000000},
            {"to_address": "DAG2...", "amount": 50000000, "fee": 200000}
        ]
        tx_hashes = await account.transfer_batch(transfers=transfers)

Send Metagraph Token
^^^^^^^^^^^^^^^^^^^^
.. note::
    :code:`Amount` and :code:`fee` are 8 decimal integers (dDAG), i.e. 1 token is equal to 100000000 units.

.. code-block:: python

