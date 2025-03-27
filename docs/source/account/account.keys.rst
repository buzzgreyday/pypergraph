Keys
====

.. admonition:: Constellation Key Trio

    An account consists of a cryptographic key trio comprising:

    - **Private Key**: A secure cryptographic element used to authenticate ownership and authorize transactions.
      Required for signing transactions and messages. **Treat as sensitive information**.
    - **Public Key**: Derived from the private key, it serves as a network identifier for node authentication and
      signature verification in trust relationships.
    - **Address**: A public wallet identifier generated from cryptographic keys. It is shareable for receiving transactions,
      while maintaining private key confidentiality.

-----

Create New Secrets
^^^^^^^^^^^^^^^^^^

Mnemonic Hierarchical Deterministic Key
---------------------------------------

.. code-block:: python

    from pypergraph.keystore import KeyStore

    # Initialize the keystore and generate a BIP-39 compliant mnemonic phrase.
    keystore = KeyStore()
    mnemonic_phrase = keystore.generate_mnemonic()


Private Key
-----------

.. code-block:: python

    from pypergraph.keystore import KeyStore

    # Generate a new private key.
    keystore = KeyStore()
    private_key = keystore.generate_private_key()

-----

Login with Existing Key
^^^^^^^^^^^^^^^^^^^^^^^

Seed Phrase
-----------

.. code-block:: python

    from pypergraph.account import DagAccount

    # Log in using a 12-word mnemonic seed phrase.
    account = DagAccount()
    account.login_with_seed_phrase("abandon abandon ...")
    account.logout()

Private Key
-----------

.. code-block:: python

    # Log in using an existing private key.
    account.login_with_private_key("private_key_here")
    account.logout()

Public Key (Read-only)
----------------------
.. note::
    Functionalities such as signing transactional data are not supported when logged in with a public key.

.. code-block:: python

    # Log in using a public key.
    account.login_with_public_key("public_key_here")
    account.logout()

-----

Get Account Keys
^^^^^^^^^^^^^^^^

After logging in, the following values become available:

DAG Address
-----------

.. code-block:: python

    # Retrieve the DAG address.
    dag_address = account.address

Public Key (Node ID)
--------------------

.. code-block:: python

    # Retrieve the public key (Node ID).
    public_key = account.public_key

Private Key
-----------
.. note::
    The private key is not available if you are logged in with a public key only.

.. code-block:: python

    # Retrieve the private key if available.
    private_key = account.private_key
