Keyrings
========

.. admonition:: Notice
   :class: note

   The :doc:`keyring manager </keyring/keyring.manager>` contains methods for easily managing wallet operations.

The keyring classes stores the account data and keys.

Hierarchical Deterministic Keyring
----------------------------------

This keyring type stores account data and keys for hierarchical deterministic (HD) wallets (see, :doc:`keyring manager </keyring/keyring.wallets>`). Here private keys (accounts) are generated from a master/root seed.
Thus, HD wallets supports multiple chains and accounts per wallet.

**Parameters**

+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                             |
+==================+======================================================+=============================================================================================+
| accounts         | ``[]`` (default) or ``list`` of ``DagAccount`` or    | Read more about account classes :doc:`here </keyring/keyring.accounts>`.                    |
|                  | ``EthAccount``                                       |                                                                                             |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| hd_path          | ``None`` (default) or ``str``                        | Path used to derive accounts from master/root key. The DAG chain has the ID 1137. Thus, the |
|                  |                                                      | DAG derivation path is "m/44'/1137'/0'/0" + the BIP44 index for the account.                |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| extended_key     | ``None`` (default) or ``str``                        | The extended key can be used to derive accounts.                                            |
|                  |                                                      |                                                                                             |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| root_key         | ``None`` (default) or ``BIP32Key``                   | Derive child (BIP index) from ``root_key`` to derive the signing key for the BIP32 account. |
|                  |                                                      | Here the package ``bip32utils`` is used.                                                    |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| network          | ``None`` (default) or ``str``                        | "Constellation" or "Ethereum".                                                              |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| mnemonic         | ``None`` (default) or ``str``                        | 12 words seed phrase.                                                                       |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+

-----

Full List of HD Keyring Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypergraph.keyring.keyrings.hd_keyring
   :members:
   :undoc-members:
   :show-inheritance:

-----

Simple Keyring
--------------

The simple keyring stores simple account data and private key. Unlike the HD keyring above, simple keyrings only supports
one private key per account.

**Parameters**

+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**    | **Type**                                             | **Description**                                                                             |
+==================+======================================================+=============================================================================================+
| account          | ``[]`` (default) or ``list`` of ``DagAccount`` or    | Read more about account classes :doc:`here </keyring/keyring.accounts>`.                    |
|                  | ``EthAccount``                                       |                                                                                             |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| network          | ``str`` = "Constellation" (default)                  | "Constellation" or "Ethereum" is currently supported.                                       |
+------------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+

-----

Full List of Simple Keyring Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypergraph.keyring.keyrings.simple_keyring
   :members:
   :undoc-members:
   :show-inheritance: