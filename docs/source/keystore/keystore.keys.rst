Keys
====

Mnemonic phrase, private keys, address, hierarchical derivation.

-----

Private Keys
^^^^^^^^^^^^

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

Get Private Key from Mnemonic
-----------------------------

Returns the first account (index: 0) from the derivation path.

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

    private_key = KeyStore().get_private_key_from_mnemonic(phrase="abandon ...", derivation_path=f"m/44'/1137'/0'/0")

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

-----

Get Extended Key Private Key from Mnemonic
------------------------------------------

Extended keys can be used to derive child keys.

**Parameters**

+-----------------------+---------------------------+
| **Parameter**         | **Type**                  |
+=======================+===========================+
| ``phrase``            | ``str``                   |
+-----------------------+---------------------------+


**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    extended_private_key = KeyStore().get_extended_private_key_from_mnemonic(phrase="abandon ...")

-----

Public Keys
^^^^^^^^^^^

Get Public Key from Private Key
-------------------------------

The public key is also used as node id.

**Parameters**

+-----------------------+---------------------------+
| **Parameter**         | **Type**                  |
+=======================+===========================+
| ``private_key``       | ``str``                   |
+-----------------------+---------------------------+


**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    public_key = KeyStore().get_public_key_from_private_key(private_key="f123...")

-----

Get DAG address from Public Key
-------------------------------

**Parameters**

+-----------------------+---------------------------+
| **Parameter**         | **Type**                  |
+=======================+===========================+
| ``public_key``        | ``str``                   |
+-----------------------+---------------------------+


**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    address = KeyStore().get_dag_address_from_public_key(public_key="f123...")

.. dropdown:: Lifecycle
   :animate: fade-in

   .. code-block:: python

      class KeyStore:

         @staticmethod
         def get_dag_address_from_public_key(public_key: str) -> str:
             """
             :param public_key: The private key as a hexadecimal string.
             :return: The DAG address corresponding to the public key (node ID).
             """
             if len(public_key) == 128:
                 public_key = PKCS_PREFIX + "04" + public_key
             elif len(public_key) == 130 and public_key[:2] == "04":
                 public_key = PKCS_PREFIX + public_key
             else:
                 raise ValueError("KeyStore :: Not a valid public key.")

             public_key = hashlib.sha256(bytes.fromhex(public_key)).hexdigest()
             public_key = base58.b58encode(bytes.fromhex(public_key)).decode()
             public_key = public_key[len(public_key) - 36 :]

             check_digits = "".join([char for char in public_key if char.isdigit()])
             check_digit = 0
             for n in check_digits:
                 check_digit += int(n)
                 if check_digit >= 9:
                     check_digit = check_digit % 9

             address = f"DAG{check_digit}{public_key}"
             return address

      address = KeyStore().get_dag_address_from_public_key(public_key="f123...")

-----

Get DAG Address from Private Key
--------------------------------

**Parameters**

+-----------------------+---------------------------+
| **Parameter**         | **Type**                  |
+=======================+===========================+
| ``private_key``       | ``str``                   |
+-----------------------+---------------------------+


**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    address = KeyStore().get_dag_address_from_private_key(private_key="f123...")

-----

Validate DAG address
--------------------

**Parameters**

+-----------------------+---------------------------+
| **Parameter**         | **Type**                  |
+=======================+===========================+
| ``address``           | ``str``                   |
+-----------------------+---------------------------+


**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    valid = KeyStore().validate_address(address="DAG1...")

.. dropdown:: Lifecycle
   :animate: fade-in

   .. code-block:: python

      class KeyStore:

         @staticmethod
         def validate_address(address: str) -> bool:
             """
             Returns True if DAG address is valid, False if invalid.

             :param address: DAG address.
             :return: Boolean value.
             """
             if not address:
                 return False

             valid_len = len(address) == 40
             valid_prefix = address.startswith("DAG")
             valid_parity = address[3].isdigit() and 0 <= int(address[3]) < 10
             base58_part = address[4:]
             valid_base58 = (
                 len(base58_part) == 36
                 and base58_part == base58.b58encode(base58.b58decode(base58_part)).decode()
             )

             return valid_len and valid_prefix and valid_parity and valid_base58

      valid_address = KeyStore().validate_address(address="DAG1...")

      if valid_address:
         print("DAG address is valid")
      else:
         print("DAG address is invalid")

----

Get ETH Address from Public Key
-------------------------------

**Parameters**

+-----------------------+---------------------------+
| **Parameter**         | **Type**                  |
+=======================+===========================+
| ``public_key``        | ``str``                   |
+-----------------------+---------------------------+


**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    address = KeyStore().get_eth_address_from_public_key(public_key="f123...")


----

Get ETH Address from Private Key
--------------------------------

**Parameters**

+-----------------------+---------------------------+
| **Parameter**         | **Type**                  |
+=======================+===========================+
| ``private_key``       | ``str``                   |
+-----------------------+---------------------------+


**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    address = KeyStore().get_eth_address_from_private_key(private_key="f123...")
