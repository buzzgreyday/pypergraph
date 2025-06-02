Keyring Wallets
===============

.. admonition:: Notice
   :class: note

   The :doc:`keyring manager </keyring/keyring.manager>` contains methods for easily managing wallet operations.

A wallet class stores one or more accounts associated with the wallet type. Each account is stored as a keyring.
There's two types of accounts stored. Hierarchical deterministic or simple keyring (see, :doc:`HdKeyring </keyring/keyrings/keyring.keyrings>`). In addition, a wallet contains a list of supported assets, which can be imported to into the :doc:`asset library </keyring/accounts/keyring.asset_library>`.

Every wallet type created will increment the ``sid`` by 1, resulting in an unique wallet ``id`` (e.g. ``MCW1``, ``SAW2``, etc.)

Multi Chain Wallet
------------------

This wallet is a hierarchical deterministic keyring type. Which means private keys (accounts) are generated from a master/root seed.
Thus, supports multiple chains and accounts per wallet.

**Parameters**

+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                             |
+==================+======================================================+=============================================================================================+
| type             | ``str``                                              | ``MCW``.                                                                                    |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| id               | ``str``                                              | Wallet type plus appended wallet iteration (e.g. ``MCW1``).                                 |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| supported_assets | ``[]`` (default) or ``list`` of ``str``              | Can be empty ``DAG`` or ``ETH``, depended on the account type associated with               |
|                  |                                                      | imported asset (see: :doc:`keyring accounts </keyring/keyring.accounts>`).                  |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| keyrings         | ``[]`` (default) or ``list`` of ``HdKeyring``        |                                                                                             |
|                  |                                                      |                                                                                             |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| label            | ``None`` (default) or ``str``                        | The name of the wallet. Maximum 12 characters.                                              |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| mnemonic         | ``None`` (default) or ``str``                        | 12 words seed phrase.                                                                       |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+

-----

Create Multi Chain Wallet
^^^^^^^^^^^^^^^^^^^^^^^^^

**Parameters**

+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                             |
+==================+======================================================+=============================================================================================+
| label            | ``str``                                              | The name of the wallet, for example ``Jane Doe 1``.                                         |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| mnemonic         | ``None`` (default) or``str``                         | 12 word seed phrase. ``None`` will create a new wallet from a new generated mnemonic seed.  |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| rings            | ``None`` (default) or ``list`` of ``HdKeyring``      | A ``HdKeyring`` object is created from the mnemonic seed phrase, hierarchical deterministic |
|                  | objects.                                             | path and the number of accounts (see: :doc:`keyring accounts </keyring/keyring.keyrings>`). |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import MultiChainWallet

    wallet = MultiChainWallet()
    wallet.create(label="Jane Doe 1")

This will store a list of hierarchical deterministic keyrings, one ``DAG`` and one ``ETH``.

-----

Get Wallet State
^^^^^^^^^^^^^^^^

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import MultiChainWallet

    wallet = MultiChainWallet()
    wallet.create(label="Jane Doe 1")
    state = wallet.get_state()

**Return**

.. code-block:: python

    {
        'id': 'MCW1',
        'type': 'MCW',
        'label': "Jane Doe 1",
        'supported_assets': [],
        'accounts': [
            {
                'address': 'DAG1...', # The DAG wallet address associated with the HD account
                'network': 'Constellation',
                'tokens': []
            },
            {
                'address': '0x1A...', # The ETH wallet address associated with the HD account
                'network': 'Ethereum',
                'tokens': ['0xa393473d64d2F9F026B60b6Df7859A689715d092']
            }
        ]
    }

-----

Full List of Multi Chain Wallet Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypergraph.keyring.wallets.multi_chain_wallet
   :members:
   :undoc-members:
   :show-inheritance:

----

Multi Account Wallet
--------------------

This wallet is a hierarchical deterministic wallet type. Which means private keys (accounts) are generated from a master/root seed.
Thus, supports multiple chains and accounts per wallet. This specific wallet type creates a number of accounts from the mnemonic seed phrase.

**Parameters**

+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                             |
+==================+======================================================+=============================================================================================+
| type             | ``str``                                              | ``MAW``.                                                                                    |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| id               | ``str``                                              | Wallet type plus appended wallet iteration (e.g. ``MAW2``).                                 |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| supported_assets | ``[]`` (default) or ``list`` of ``str``              | Can be empty ``DAG`` or ``ETH``, depended on the account type associated with               |
|                  |                                                      | imported asset (see: :doc:`keyring accounts </keyring/keyring.accounts>`).                  |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| keyring          | ``None`` (default) or ``HdKeyring``                  |                                                                                             |
|                  |                                                      |                                                                                             |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| label            | ``None`` (default) or ``str``                        | The name of the wallet. Maximum 12 characters.                                              |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| network          | ``None`` (default) or ``str``                        | ``Constellation`` or ``Ethereum``.                                                          |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| mnemonic         | ``None`` (default) or ``str``                        | 12 words seed phrase.                                                                       |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+

-----

Create Multi Account Wallet
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Parameters**

+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                             |
+==================+======================================================+=============================================================================================+
| label            | ``str``                                              | The name of the wallet, for example ``Jane Doe 2``.                                         |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| mnemonic         | ``None`` (default) or ``str``                        | 12 word seed phrase. ``None`` will create a new wallet from a new generated mnemonic seed.  |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| num_of_accounts  | ``int`` = 1 (default)                                | Number of BIP44 indexes (accounts) to create using the mnemonic phrase.                     |
|                  |                                                      |                                                                                             |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| network          | ``str``                                              | ``Constellation`` or ``Ethereum``.                                                          |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import MultiAccountWallet

    wallet = MultiAccountWallet()
    wallet.create(network="Constellation", label="Jane Doe 4", num_of_accounts=3)
    state = wallet.get_state()

**Return**

.. code-block:: python

    {
        'id': 'MAW4',
        'type': 'MAW',
        'label': 'Jane Doe 4',
        'supported_assets': ['DAG'],
        'accounts': [
            {
                'address': 'DAG1ZHaLNLDJoV7yAvjbvLTTKXzHX1A18xEd2zoc', # DAG address corresponding to mnemonic phrase BIP44 index 0
                'supported_assets': ['DAG']
            },
            {
                'address': 'DAG0mUMDdcQrNnzvZJ7RiY7C5LUUiPBh8YvnAffe', # ... BIP44 index 1
                'supported_assets': ['DAG']
            },
            {
                'address': 'DAG4q9htCP4CuBo2iPDVRMHxF5cR7fHM4ovfukQe', # ... BIP44 index 2
                'supported_assets': ['DAG']
            }
        ]
    }


-----

Full List of Multi Chain Wallet Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypergraph.keyring.wallets.multi_account_wallet
   :members:
   :undoc-members:
   :show-inheritance:

----

Single Account Wallet
---------------------

This wallet is **not** a hierarchical deterministic wallet type. Which means the private keys are not
generated from a master/root seed. Does **not** support multiple chains and accounts per wallet secret, one
private key per account and/or chain.

**Parameters**

+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                                | **Description**                                                                             |
+==================+=========================================================+=============================================================================================+
| type             | ``str``                                                 | ``SAW``.                                                                                    |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| id               | ``str``                                                 | Wallet type plus appended wallet iteration (e.g. ``SAW3``).                                 |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| supported_assets | ``[]`` (default) or ``list`` of ``str``                 | Can be empty ``DAG`` or ``ETH``, depended on the account type associated with               |
|                  |                                                         | imported asset (see: :doc:`keyring accounts </keyring/keyring.accounts>`).                  |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| keyring          | ``None`` (default) or ``SimpleKeyring``                 |                                                                                             |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| network          | ``None`` (default) or ``str``                           | ``Constellation`` or ``Ethereum``.                                                          |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| label            | ``None`` (default) or ``str``                           | The name of the wallet. Maximum 12 characters.                                              |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+

-----

Create Single Account Wallet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Parameters**

+------------------+------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                                                                  |
+==================+======================================================+==================================================================================================================================+
| label            | ``str``                                              | The name of the wallet, for example ``Jane Doe 3``.                                                                              |
+------------------+------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| private_key      | ``None`` (default) or ``str``                        | The private key you wish to create an account/wallet for. ``None`` will create a new wallet from a new generated mnemonic seed.  |
+------------------+------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| network          | ``str``                                              | ``Constellation`` or ``Ethereum``.                                                                                               |
+------------------+------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import SingleAccountWallet

    wallet = SingleAccountWallet()
    wallet.create(label="Jane Doe 2")
    state = wallet.get_state()

**Return**

.. code-block:: python

   {
        'id': 'SAW2',
        'type': 'SAW',
        'label': 'Jane 2',
        'supported_assets': ['DAG'],
        'accounts': [
            {
                'address': 'DAG6pmeo33ykpedwVaZqnQo7Kz7x4HUuL9PiqdJH', # The DAG address associated with the wallet/account private key
                'network': 'Constellation',
                'tokens': []
            }
        ]
   }

-----

Full List of Single Account Wallet Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypergraph.keyring.wallets.single_account_wallet
   :members:
   :undoc-members:
   :show-inheritance:

-----

Multi Key Wallet
----------------

This wallet is **not** a hierarchical deterministic wallet type. Which means the private keys are not
generated from a master/root seed.

This wallet type **does not** automatically generate a new account/wallet. Instead, simple accounts (private key accounts)
are imported into the wallet manually after creation. For each import a ``label`` and ``network`` is provided and the imported
private key is added to the list of keyrings.

**Parameters**

+------------------+------------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                                   | **Description**                                                                             |
+==================+============================================================+=============================================================================================+
| type             | ``str``                                                    | ``MKW``.                                                                                    |
+------------------+------------------------------------------------------------+---------------------------------------------------------------------------------------------+
| id               | ``str``                                                    | Wallet type plus appended wallet iteration (e.g. ``MKW4``).                                 |
+------------------+------------------------------------------------------------+---------------------------------------------------------------------------------------------+
| supported_assets | ``[]`` (default) or ``list`` of ``str``                    | Can be empty ``DAG`` or ``ETH``, depended on the account type associated with               |
|                  |                                                            | imported asset (see: :doc:`keyring accounts </keyring/keyring.accounts>`).                  |
+------------------+------------------------------------------------------------+---------------------------------------------------------------------------------------------+
| keyrings         | ``[]`` (default) or ``list`` of SimpleKeyring``            |                                                                                             |
+------------------+------------------------------------------------------------+---------------------------------------------------------------------------------------------+
| network          | ``None`` (default) or ``str``                              | ``Constellation`` or ``Ethereum``.                                                          |
+------------------+------------------------------------------------------------+---------------------------------------------------------------------------------------------+
| label            | ``None`` (default) or ``str``                              | The name of the wallet. Maximum 12 characters.                                              |
+------------------+------------------------------------------------------------+---------------------------------------------------------------------------------------------+

-----

Create Multi Key Wallet
^^^^^^^^^^^^^^^^^^^^^^^

Creates an empty wallet by default. Manual import necessary, see method below.

**Parameters**

+------------------+------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                                                                  |
+==================+======================================================+==================================================================================================================================+
| label            | ``str``                                              | The name of the wallet, for example ``Jane Doe 4``.                                                                              |
+------------------+------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+
| network          | ``str``                                              | ``Constellation`` or ``Ethereum``.                                                                                               |
+------------------+------------------------------------------------------+----------------------------------------------------------------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import MultiKeyWallet

    wallet = MultiKeyWallet()
    wallet.create(label="Jane Doe 3", network="Constellation")
    wallet.import_account(private_key="469f...", label="Account 1")
    wallet.get_state()

**Return**

.. code-block:: python

    {
        'id': 'MKW3',
        'type': 'MKW',
        'label': 'Jane Doe 3',
        'network': 'Constellation',
        'supported_assets': ['DAG'],
        'accounts': [
            {
                'address': 'DAG6s6X8BGsLysM6yGtntpkuwKo52QLbTibP6uCR', # The DAG address associated with the private key
                'label': 'Account 1'
            }
        ]
    }

-----

Full List of Multi Key Wallet Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypergraph.keyring.wallets.multi_key_wallet
   :members:
   :undoc-members:
   :show-inheritance: