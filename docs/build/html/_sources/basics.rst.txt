Basics
======

* **CREATE NEW WALLET**

.. code-block:: python

    wallet = Wallet.new()

* **IMPORT WALLET FROM MNEMONIC PHRASE**

.. code-block:: python

    wallet = Wallet.from_mnemonic("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon")

* **IMPORT WALLET FROM PRIVATE KEY**

.. code-block:: python

    wallet = Wallet.from_private_key("SOME_VALID_PRIVATE_KEY")

* **GET DAG WALLET ADDRESS**

.. code-block:: python

    public_key = wallet.public_key

* **GET DAG WALLET PRIVATE KEY**

.. code-block:: python

    private_key = wallet.private_key

* **GET DAG WALLET MNEMONIC PHRASE**

.. code-block:: python

    words = wallet.words

* **GET DAG WALLET BALANCE**

    **Default:** `dag_address=wallet.address, metagraph_id=None`

.. code-block:: python

    balance = await wallet.get_address_balance()

* **SET NON-DEFAULT DAG WALLET NETWORK**

    **Default:** `network="mainnet", layer=1, host=None, metagraph_id=None`

.. code-block:: python

    wallet = wallet.set_network(network="testnet", layer=1)

* **NEW TRANSACTION**

.. code-block:: python

    tx = await wallet.transaction(to_address='SOME_VALID_DAG_ADDRESS', amount=1.0, fee=0.0002)

* **SEND TRANSACTION**

.. code-block:: python

    response = await wallet.send(tx)

* **GET PENDING TRANSACTION**

    **Default:** returns an object if transaction is pending, None if transaction has been processed.

.. code-block:: python

   import asyncio

   async def check_pending_transaction(wallet):
       while True:
           pending = await wallet.get_pending_transaction(hash)
           if not pending:
               break
           await asyncio.sleep(5)
       print("Transaction sent.")
