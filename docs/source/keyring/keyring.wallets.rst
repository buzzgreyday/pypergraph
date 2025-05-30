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
