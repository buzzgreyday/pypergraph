Other Methods
=============

All methods can be found here :doc:`account package </pypergraph.account>`.

-----

Check Pending Transaction
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio

    async def accepted(tx: PendingTransaction) -> bool:
        """
        Wait until the given transaction is accepted in a checkpoint.

        Args:
            tx (PendingTransaction): A PendingTransaction instance.

        Returns:
            bool: True when the transaction is accepted.
        """
        while not await account.wait_for_checkpoint_accepted(tx.hash):
            await asyncio.sleep(6)  # Prevent busy-waiting
        return True

    async def main():
        # Initiate a transfer which returns a pending transaction.
        pending_transaction = await account.transfer(
            to_address="DAG1...",
            amount=100000000,  # 1 DAG = 10^8 units
            fee=200000
        )

        # Check if the transaction has been accepted.
        if await accepted(pending_transaction):
            print("Accepted:", pending_transaction.hash)

    # Execute the async main function.
    asyncio.run(main())

-----

Check Account Balance Change
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio

    async def wait_for_balance_change():
        """
        Wait for the account balance to change and print a message.
        """
        if await account.wait_for_balance_change():
            print("Balance changed.")

    async def main():
        await wait_for_balance_change()

    # Execute the async main function.
    asyncio.run(main())

-----

Get Account Balance
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Retrieve the current account balance.
    balance = account.get_balance()
    print("Account Balance:", balance)

-----

Get Address Balance
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Retrieve the balance for a specific address.
    balance = account.get_balance_for("DAG1...")
    print("Address Balance:", balance)
