Store Secrets
=============

Placeholder

-----

Encrypt Private Key
-------------------

Returns dictionary, use ``json.dumps()`` and write to file to transfer account between wallets.

**Parameters**

+---------------------+----------------------------------+--------------------------------------------+
| **Parameter**       | **Type**                         | **Description**                            |
+=====================+==================================+============================================+
| ``private_key``     | ``str``                          | Account private key                        |
+---------------------+----------------------------------+--------------------------------------------+
| ``password``        | ``str``                          | Wallet password                            |
+---------------------+----------------------------------+--------------------------------------------+

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    v3_keystore = await KeyStore().encrypt_phrase(phrase="abandon ...", password="password123")

-----

Decrypt Private Key
-------------------

Returns the account private key as ``str``.

**Parameters**

+---------------------+----------------------------------+--------------------------------------------+
| **Parameter**       | **Type**                         | **Description**                            |
+=====================+==================================+============================================+
| ``data``            | ``dict``                         | Encrypted private key store.               |
+---------------------+----------------------------------+--------------------------------------------+
| ``password``        | ``str``                          | Wallet password                            |
+---------------------+----------------------------------+--------------------------------------------+

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    private_key = await KeyStore().decrypt_phrase(data=v3_keystore, password="password123")

-----

Validate Private Key Keystore
-----------------------------

Returns ``bool``.

+---------------------+----------------------------------+--------------------------------------------+
| **Parameter**       | **Type**                         | **Description**                            |
+=====================+==================================+============================================+
| ``data``            | ``dict``                         | Validate keystore dictionary               |
+---------------------+----------------------------------+--------------------------------------------+

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    valid_keystore = KeyStore().validate_private_key_keystore(data=v3_keystore)

    if valid_keystore:
        print("Keystore is valid.")
    else:
        print("Keystore is invalid.")

-----

Encrypt Phrase
--------------

Can be used to lock wallet, if wallet is inactive.

Returns ``V3Keystore`` object.

**Parameters**

+---------------------+----------------------------------+--------------------------------------------+
| **Parameter**       | **Type**                         | **Description**                            |
+=====================+==================================+============================================+
| ``phrase``          | ``str``                          | 12 words mnemonic phrase                   |
+---------------------+----------------------------------+--------------------------------------------+
| ``password``        | ``str``                          | Wallet password                            |
+---------------------+----------------------------------+--------------------------------------------+

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    v3_keystore = await KeyStore().encrypt_phrase(phrase="abandon ...", password="password123")

-----

Decrypt Phrase
--------------

Can be used to unlock secret when wallet is activated.

Returns the decrypted phrase.

**Parameters**

+---------------------+----------------------------------+--------------------------------------------+
| **Parameter**       | **Type**                         | **Description**                            |
+=====================+==================================+============================================+
| ``keystore``        | ``V3Keystore``                   | Encrypted ``V3Keystore`` object            |
+---------------------+----------------------------------+--------------------------------------------+
| ``password``        | ``str``                          | Wallet password                            |
+---------------------+----------------------------------+--------------------------------------------+

**Example Code**

.. code-block:: python

    from pypergraph import KeyStore

    phrase = await KeyStore().decrypt_phrase(keystore=v3_keystore, password="password123")
