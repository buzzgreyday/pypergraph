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

    Default: returns a single float value

.. code-block:: python

    balance = await wallet.get_address_balance()

* **SET NON-DEFAULT DAG WALLET API**

    Default: network="mainnet", layer=1

.. code-block:: python

    wallet = wallet.set_api(network="testnet", layer=1)

* **NEW TRANSACTION**

.. code-block:: python

    tx = await wallet.transaction(to_address='SOME_VALID_DAG_ADDRESS', amount=1.0, fee=0.0002)

* **SEND TRANSACTION**

.. code-block:: python

    response = await wallet.send(tx)
