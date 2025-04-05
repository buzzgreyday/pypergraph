Balance
=======

Placeholder.

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

