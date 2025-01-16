Basics
======

Pypergraph Wallets
------------------
A Pypergraph wallet is basically a Constellation ``key trio`` with the addition of a ``words`` variable (the mnemonic phrase) and a ``network`` object variable with the current network configuration of the ``wallet`` object.

.. note::
    In the Pypergraph package, ``accounts`` are referred to as ``wallets``. Wallet methods can be imported from :class:`pypergraph.dag_wallet.Wallet` and key related methods from :class:`pypergraph.dag_keystore.KeyStore`.

.. dropdown:: The Constellation Key Trio
    :animate: fade-in

    In the Constellation Network, accounts (or wallets) are composed of a key trio consisting of the private key, public key, and a DAG address.

    .. tab-set::

        .. tab-item:: Private key

            The private key is a highly confidential piece of information that plays a crucial role in authenticating an address to the network. With the private key, you can execute sensitive actions like signing messages or sending transactions.


        .. tab-item:: Public key

            The public key serves as a unique identifier for nodes on the network and is derived from the private key. It is crucial for establishing trust relationships between nodes, enabling secure communication, and verifying digital signatures.


        .. tab-item:: Address

            The address is the public-facing component of the Key Trio and represents a public wallet address for receiving payments or other digital transactions. It can be derived from either the private or public key and is widely used for peer-to-peer transactions. Sharing your address with others enables them to send you payments while keeping your private key confidential.

    Source: `Accounts and Keys <https://docs.constellationnetwork.io/metagraphs/accounts/>`_

------

* **CREATE NEW WALLET**

.. code-block:: python

    wallet = Wallet.new()

.. dropdown:: How is a new wallet object created?
    :animate: fade-in

    .. code-block:: python

        from pypergraph.dag_keystore import KeyStore

        mnemonic_values = KeyStore.get_mnemonic()
        private_key = KeyStore.get_private_key_from_seed(seed=mnemonic_values["seed"])
        public_key = KeyStore.get_public_key_from_private_key(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key=public_key)
        valid = KeyStore.validate_dag_address(address=address)
        if not valid:
            raise ValueError("Wallet :: Not a valid DAG address.")

-----

* **IMPORT WALLET FROM MNEMONIC PHRASE**

.. code-block:: python

    wallet = Wallet.from_mnemonic("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon")

.. dropdown:: How is the private key, public key and DAG address derived from mnemonic phrase?
    :animate: fade-in

    The private key, public key and DAG address is generated from a 12 word seed.

    .. code-block:: python

        from pypergraph.dag_keystore import KeyStore, Bip39

        valid = KeyStore.validate_mnemonic(mnemonic_phrase=words)
        if not valid:
            raise ValueError("Wallet :: Not a valid mnemonic.")
        mnemonic = Bip39()
        seed_bytes = mnemonic.get_seed_from_mnemonic(words)
        private_key = KeyStore.get_private_key_from_seed(seed_bytes)
        public_key = KeyStore.get_public_key_from_private_key(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        valid = KeyStore.validate_dag_address(address=address)
        if not valid:
            raise ValueError("Wallet :: Not a valid DAG address.")

-----

* **IMPORT WALLET FROM PRIVATE KEY**

.. code-block:: python

    wallet = Wallet.from_private_key("SOME_VALID_PRIVATE_KEY")

.. dropdown:: How is the public key and DAG address derived from a private key?
    :animate: fade-in

    .. code-block:: python

        from pypergraph.dag_keystore import KeyStore

        public_key = KeyStore.get_public_key_from_private_key(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        valid = KeyStore.validate_dag_address(address=address)
        if not valid:
            raise ValueError("Wallet :: Not a valid DAG address.")

-----

* **GET DAG WALLET MNEMONIC PHRASE**

.. code-block:: python

    words = wallet.words

-----

* **GET DAG WALLET PRIVATE KEY**

.. code-block:: python

    private_key = wallet.private_key

-----

* **GET DAG WALLET PUBLIC KEY**

.. code-block:: python

    dag_address = wallet.public_key

------

* **GET DAG WALLET ADDRESS**

.. code-block:: python

    dag_address = wallet.address

.. dropdown:: How is a DAG address generated from a public key?
    :animate: fade-in

    The DAG address is derived from the public key and stored in the ``wallet.address`` object variable.

    .. code-block:: python

        import base58
        from hashlib import sha256

        PKCS_PREFIX = "3056301006072a8648ce3d020106052b8104000a034200"

        if len(public_key_hex) == 128:
            public_key = PKCS_PREFIX + "04" + public_key_hex
        elif len(public_key_hex) == 130 and public_key_hex[:2] == "04":
            public_key = PKCS_PREFIX + public_key_hex
        else:
            raise ValueError("Not a valid public key")

        public_key = sha256(bytes.fromhex(public_key)).hexdigest()
        public_key = base58.b58encode(bytes.fromhex(public_key)).decode()
        public_key = public_key[len(public_key) - 36:]

        check_digits = "".join([char for char in public_key if char.isdigit()])
        check_digit = 0
        for n in check_digits:
            check_digit += int(n)
            if check_digit >= 9:
                check_digit = check_digit % 9

        address = f"DAG{check_digit}{public_key}"

-----

* **GET DAG WALLET BALANCE**

    **Default:** `dag_address=wallet.address, metagraph_id=None`

.. code-block:: python

    balance = await wallet.get_address_balance()

-----

* **SET NON-DEFAULT DAG WALLET NETWORK**

  Reconfigures the ``wallet.network`` object variable used to handle interaction with Constellation APIs. The parameters ``l0_host`` and ``l1_host`` is required if ``metagraph_id`` is set.

    **Default:** `network="mainnet", l0_host=None, l1_host=None, metagraph_id=None`

.. code-block:: python

    wallet = wallet.set_network(network="testnet")

-----

Pypergraph Transactions
-----------------------

* **NEW TRANSACTION**

.. code-block:: python

    tx = await wallet.transaction(to_address='SOME_VALID_DAG_ADDRESS', amount=1.0, fee=0.0002)

.. dropdown:: How is a transaction created?
   :animate: fade-in

   .. code-block:: python

       last_ref = await self.network.get_last_reference(address_hash=self.address)
       tx, tx_hash, encoded_tx = KeyStore.prepare_tx(amount=amount, to_address=to_address, from_address=self.address,
                                                     last_ref=last_ref.to_dict(), fee=fee)
       signature = KeyStore.sign(private_key_hex=self.private_key, tx_hash=tx_hash)
       valid = KeyStore.verify(public_key_hex=self.public_key, tx_hash=tx_hash, signature_hex=signature)
       if not valid:
           raise ValueError("Wallet :: Invalid signature.")
       proof = {"id": self.public_key[2:], "signature": signature}
       tx.add_proof(proof=proof)

-----

* **SEND TRANSACTION**

.. code-block:: python

    response = await wallet.send(tx)

-----

* **GET PENDING TRANSACTION**

    **Default:** returns an object if transaction is pending, None if transaction has been processed.

.. code-block:: python

    pending = await wallet.get_pending_transaction(hash)

.. dropdown:: How can I check if a transaction has been sent?
    :animate: fade-in

    The following code is an example of how to check if the transaction is processed or not.

    .. code-block:: python

       import asyncio

       async def check_pending_transaction(wallet):
           while True:
               pending = await wallet.get_pending_transaction(hash)
               if not pending:
                   break
               await asyncio.sleep(5)
           print("Transaction sent.")
