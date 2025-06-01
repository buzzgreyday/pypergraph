Wallets
=======

The :doc:`keyring manager </keyring/keyring.manager>` contains methods for easily retrieving wallets associated with a given address or wallet ID.
This will return one or more objects of the classes below.

A wallet contains a list of supported assets, which can be imported to into the :doc:`asset library </keyring/accounts/keyring.asset_library>`. A name ``label``.
Minimum one keyring of type :doc:`HdKeyring </keyring/keyrings/keyring.hd_keyring>` or :doc:`SimpleKeyring </keyring/keyrings/keyring.simple_keyring>`

Every wallet type created will increment the ``sid`` by +1, resulting in an unique wallet ``id`` (e.g. ``MCW1``, ``SAW2``, etc.) Each wallet also has the ability to reset ``sid``

.. admonition:: Notice
   :class: note

   Most wallet methods can be used from the :doc:`KeyringManager </keyring/keyring.manager>`.

Multi Chain Wallet
------------------

This wallet is a hierarchical deterministic wallet type. Which means private keys are generated from a master/root seed.
Thus, supports multiple chains and accounts per wallet.

**Parameters**

+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                             |
+==================+======================================================+=============================================================================================+
| type             | ``str``                                              | ``MCW``.                                                                                    |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| id               | ``str``                                              | Wallet type plus appended wallet iteration (e.g. ``MCW1``).                                 |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| supported_assets | ``List[None]`` (default) or ``list`` of ``str``      | Can be empty ``DAG`` or ``ETH``, depended on the account type associated with               |
|                  |                                                      | imported asset (see: :doc:`keyring accounts </keyring/keyring.accounts>`).                  |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| keyrings         | ``List[None]`` (default) or list of ``HdKeyring()``  |                                                                                             |
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
| label            | ``str``                                              | For example ``Jane Doe's Wallet``.                                                          |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| mnemonic         | ``None`` (default) or``str``                         | 12 word seed phrase. ``None`` will create a new wallet from a new generated mnemonic seed.  |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| rings            | ``None`` (default) or ``list`` of ``HdKeyring()``    | A ``HdKeyring`` object is created from the mnemonic seed phrase, hierarchical deterministic |
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
    print(state)

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

-----

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
| id               | ``str``                                                 | Wallet type plus appended wallet iteration (e.g. ``SAW2``).                                 |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| supported_assets | ``List[None]`` (default) or ``list`` of ``str``         | Can be empty ``DAG`` or ``ETH``, depended on the account type associated with               |
|                  |                                                         | imported asset (see: :doc:`keyring accounts </keyring/keyring.accounts>`).                  |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| keyring          | ``List[None]`` (default) or list of ``SimpleKeyring()`` |                                                                                             |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| network          | ``None`` (default) or ``str``                           | ``Constellation`` or ``Ethereum``.                                                          |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+
| label            | ``None`` (default) or ``str``                           | The name of the wallet. Maximum 12 characters.                                              |
+------------------+---------------------------------------------------------+---------------------------------------------------------------------------------------------+

-----

Create Single Account Wallet
----------------------------

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import SingleAccountWallet

    wallet = SingleAccountWallet()
    wallet.create(label="Jane Doe 2")

-----

Get Wallet State
^^^^^^^^^^^^^^^^

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import SingleAccountWallet

    wallet = SingleAccountWallet()
    wallet.create(label="Jane Doe 2")
    state = wallet.get_state()
    print(state)

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

Full List of Single Account Wallet Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypergraph.keyring.wallets.single_account_wallet
   :members:
   :undoc-members:
   :show-inheritance: