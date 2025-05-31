Wallets
=======

The :doc:`keyring manager </keyring/keyring.manager>` contains methods for easily retrieving wallets associated with a given address or wallet ID.
This will return one or more objects of the classes below.

A wallet contains a list of supported assets, which can be imported to into the :doc:`asset library </keyring/accounts/keyring.asset_library>`. A name ``label``.
Minimum one keyring of type :doc:`HdKeyring </keyring/keyrings/keyring.hd_keyring>` or :doc:`SimpleKeyring </keyring/keyrings/keyring.simple_keyring>`

.. admonition:: Notice
   :class: note

   Most wallet methods can be used from the :doc:`KeyringManager </keyring/keyring.manager>`.

Multi Chain Wallet
------------------

This wallet is a hierarchical deterministic wallet type.

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
| mnemonic         | ``None`` (default) or``str``                         | 12 word seed phrase. ``None`` will generate a new mnemonic seed.                            |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| rings            | ``None`` (default) or ``list`` of ``HdKeyring()``    | A ``HdKeyring`` object is created from the mnemonic seed phrase, hierarchical deterministic |
|                  | objects.                                             | path and the number of accounts (see: :doc:`keyring accounts </keyring/keyring.keyrings>`). |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import MultiChainWallet

    wallet = MultiChainWallet()
    wallet.create(label="Jane Doe's Wallet")

This will store a list of hierarchical deterministic keyrings, one ``DAG`` and one ``ETH``.

-----

Get Wallet State
^^^^^^^^^^^^^^^^

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import MultiChainWallet

    wallet = MultiChainWallet()
    wallet.create(label="Jane Doe's Wallet", mnemonic="abandon abandon ... ")
    state = wallet.get_state()
    print(state)

**Return**

.. code-block:: python

    {
        'id': 'MCW4',
        'type': 'MCW',
        'label': "Jane Doe's Wallet",
        'supported_assets': [],
        'accounts': [
            {'address': 'DAG0zJW14beJtZX2BY2KA9gLbpaZ8x6vgX4KVPVX', 'network': 'Constellation', 'tokens': []},
            {'address': '0x8Fbc948ba2dD081A51036dE02582f5DcB51a310c', 'network': 'Ethereum', 'tokens': ['0xa393473d64d2F9F026B60b6Df7859A689715d092']}
        ]
    }

-----

Full List of Multi Chain Wallet Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypergraph.keyring.wallets.multi_chain_wallet
   :members:
   :undoc-members:
   :show-inheritance: