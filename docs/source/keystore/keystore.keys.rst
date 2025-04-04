Keys
====

Mnemonic phrase, private keys, address, hierarchical derivation.

-----

Private Keys
^^^^^^^^^^^^

-----

Generate Mnemonic
-----------------

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    mnemonic_phrase = KeyStore().generate_mnemonic()

Validate Mnemonic
-----------------

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    valid_mnemonic = KeyStore().validate_mnemonic(phrase="abandon ...") # 12 words

    if not valid_mnemonic:
        print("Invalid mnemonic.")
    else:
        print("Valid Mnemonic.")

-----

Generate Private Key
--------------------

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    private_key = KeyStore().generate_private_key()

-----

Get Master Key from Mnemonic Phrase
-----------------------------------

**Parameters**

+---------------------+----------------------------------+--------------------------------------------+
| **Parameter**       | **Type**                         | **Description**                            |
+=====================+==================================+============================================+
| ``phrase``          | ``str``                          | 12 words mnemonic phrase                   |
+---------------------+----------------------------------+--------------------------------------------+
| ``derivation_path`` | ``str`` without index.           | DAG and ETH ``derivation paths`` and       |
|                     | ``f"m/44'/1137'/0'/0" (default)``| ``coin type`` i can be imported from       |
|                     |                                  | ``pypergraph.core.constants``              |
+---------------------+----------------------------------+--------------------------------------------+

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    master_key = KeyStore().get_master_key_from_mnemonic(phrase="abandon ...", derivation_path=f"m/44'/1137'/0'/0")

-----

Derive Private Key from Master Key
----------------------------------

This will derive a private key (account) from a hierarchical deterministic master key.

**Parameters**

+-----------------------+---------------------------+---------------------------------------------------------------+
| **Parameter**         | **Type**                  | **Description**                                               |
+=======================+===========================+===============================================================+
| ``master_key``        | ``BIP32Key``              |                                                               |
+-----------------------+---------------------------+---------------------------------------------------------------+
| ``index``             | ``int``: ``0 (default)``. | Derive the private key of account index number ``X``.         |
+-----------------------+---------------------------+---------------------------------------------------------------+

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    private_key = KeyStore().derive_account_from_master_key(master_key=master_key, index=0)

