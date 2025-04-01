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

New secrets are generated using methods imported from the sub-package ``keystore``. For an in-depth documentation of the ``keystore`` sub-package, see [missing link].

Mnemonic Hierarchical Deterministic Key
---------------------------------------

.. code-block:: python

    from pypergraph import KeyStore

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

Private Key
-----------
.. note::
    The private key is not available if you are logged in with a public key only.

.. code-block:: python

    # Retrieve the private key if available.
    private_key = account.private_key

Public Key (Node ID)
--------------------

.. code-block:: python

    # Retrieve the public key (Node ID).
    public_key = account.public_key

DAG Address
-----------

.. code-block:: python

    # Retrieve the DAG address.
    dag_address = account.address

.. dropdown:: Generate DAG Address Lifecycle
    :animate: fade-in

    See keystore [missing link].

    .. code-block:: python

        from pypergraph import DagAccount

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

        account = DagAccount()

        dag_address = account.get_dag_address_from_public_key(account.public_key)
