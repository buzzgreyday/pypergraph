Basics
======

Create Account/Wallet
_____________________

In Pypergraph, wallets are referred to as accounts.

Create New Account/Wallet
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_keystore import KeyStore
    from pypergraph.dag_account import DagAccount

    keystore = KeyStore()

    # Generate a new mnemonic seed phrase
    mnemonic = keystore.get_mnemonic()
    seed_phrase = mnemonic

    # Store the seed phrase securely before proceeding
    account = DagAccount()
    account.login_with_seed_phrase(words=seed_phrase)

    # Example: Print the generated public address
    print("DAG Address:", account.address)

Create Account from Existing Secret
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_account import DagAccount

    # Use your existing seed phrase or private key
    seed_phrase = "abandon abandon ..." # 12 words seed phrase
    account = DagAccount()
    account.login_with_seed_phrase(words=seed_phrase)

.. dropdown:: Login Variations
    :animate: fade-in

    * **Login with Seed Phrase**

    .. code-block:: python

        account.login_with_seed_phrase("abandon abandon ..." )

    * **Login with Private Key**

    .. code-block:: python

        account.login_with_private_key("your_private_key_here")

    * **Login with Public Key**

    .. note::

        Private key is required to send transactions. Public key login allows read-only access.

    .. code-block:: python

        account.login_with_public_key("your_public_key_here")

Send Transactions
_________________

Send $DAG Currency Transaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Create and login to account
    seed_phrase = "abandon abandon ..." # 12 words seed phrase
    account = DagAccount()
    account.login_with_seed_phrase(seed_phrase)
    hash = await account.transfer(to_address=to_address, amount=100000000, fee=200000)

**Or...**

.. code-block:: python

    import asyncio
    from pypergraph.dag_account import DagAccount

    async def send_dag():
        # Create and login to account
        seed_phrase = "abandon abandon ..." # 12 words seed phrase
        account = DagAccount()
        account.login_with_seed_phrase(words=seed_phrase)

        # Connect to testnet (default: mainnet)
        account.connect(network_id="testnet")

        # Generate and send transaction
        tx, tx_hash = await account.generate_signed_transaction(
            to_address="DAG2this01is02A03FAKE04DAG05Address06",
            amount=100000000,  # 1 DAG = 100,000,000 units
            fee=200000
        )
        await account.network.post_transaction(tx)
        print("Transaction Hash:", tx_hash)

    asyncio.run(send_dag())

.. dropdown:: Transaction Building and Signing
    :animate: fade-in

    .. code-block:: python

        def prepare_tx(
                amount: int,
                to_address: str,
                from_address: str,
                last_ref: LastReference,
                fee: int = 0
                ) -> Tuple[Transaction, str]:

            if to_address == from_address:
              raise ValueError('KeyStore :: An address cannot send a transaction to itself')

            if int(amount) < 1e-8:
              raise ValueError('KeyStore :: Send amount must be greater than 1e-8')

            if fee < 0:
              raise ValueError('KeyStore :: Send fee must be greater or equal to zero')

            # Create transaction
            tx = Transaction(
                source=from_address, destination=to_address, amount=amount, fee=fee,
                parent=last_ref, salt=MIN_SALT + int(random.getrandbits(48))
            )

            # Get encoded transaction
            encoded_tx = tx.encoded

            kryo = Kryo()
            serialized_tx = kryo.serialize(msg=encoded_tx, set_references=False)
            hash_value = KeyStore._double_hash(serialized_tx)

            return tx, hash_value

        async def generate_signed_transaction(
                self,
                to_address: str,
                amount: int,
                fee: int = 0,
                last_ref=None
        ) -> Tuple[SignedTransaction, str]:
            last_ref = last_ref or await self.network.get_address_last_accepted_transaction_ref(self.address)
            tx, hash_ = KeyStore.prepare_tx(
                amount=amount,
                to_address=to_address,
                from_address=self.key_trio.address,
                last_ref=last_ref,
                fee=fee
            )
            signature = KeyStore.sign(self.key_trio.private_key, hash_)
            valid = KeyStore.verify(self.public_key, hash_, signature)
            if not valid:
                raise ValueError("Wallet :: Invalid signature.")
            proof = SignatureProof(id=self.public_key[2:], signature=signature)
            tx = SignedTransaction(value=tx, proofs=[proof])
            return tx, hash_

        # Generate and send transaction
        tx, tx_hash = await account.generate_signed_transaction(
            to_address="DAG2this01is02A03FAKE04DAG05Address06",
            amount=100000000,  # 1 DAG = 100,000,000 units
            fee=200000
        )

.. dropdown:: DagAccount Network Parameters
    :animate: fade-in

    Configure network endpoints when calling ``account.connect()``:

    * **Network_id**

        Supported values: ``"mainnet"``, ``"testnet"``, ``"integrationnet"``.

    * **be_url**

        Override the default Blockchain Explorer URL (``"https://be-{network_id}.constellationnetwork.io"``).

    Other parameters (``l0_url``, ``cl1_url``, etc.) follow similar patterns.

Send Metagraph Currency Transaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio
    from pypergraph.dag_account import MetagraphTokenClient

    async def send_metagraph_token():
        account = DagAccount()
        account.login_with_seed_phrase("your_seed_phrase")

        # Initialize Metagraph client
        metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43",
            l0_host="http://custom-l0-host:9100",  # Replace with actual endpoints
            cl1_host="http://custom-cl1-host:9200"
        )

        # Get last transaction reference for the sender
        last_ref = await metagraph_client.network.get_address_last_accepted_transaction_ref(
            address=account.address  # Use the account's address
        )

        # Generate and send transaction
        tx, tx_hash = await metagraph_client.account.generate_signed_transaction(
            to_address="DAG2RecipientAddress...",
            amount=100000000,
            fee=0,  # Metagraphs may have custom fee rules
            last_ref=last_ref
        )
        await metagraph_client.network.post_transaction(tx)
        print("Metagraph Transaction Hash:", tx_hash)

    asyncio.run(send_metagraph_token())

Send Metagraph Data Transaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import asyncio
    import json
    from pypergraph.dag_keystore import KeyStore

    async def send_data_transaction():
        keystore = KeyStore()
        seed_phrase = "abandon abandon ... " # 12 word seed phrase
        private_key = keystore.get_private_key_from_mnemonic(phrase=seed_phrase)

        account = DagAccount()
        account.login_with_seed_phrase(words=seed_phrase)

        # Initialize Metagraph client
        metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG6DOES00NOT00MATTER00HERE",
            l0_host="http://localhost:9200",
            cl1_host="http://localhost:9300"
        )

        # Prepare data payload
        tx_data = {
            "CreatePoll": {
                "name": "test_poll",
                "owner": account.address,
                "pollOptions": ["true", "false"],
                "startSnapshotOrdinal": 1000,
                "endSnapshotOrdinal": 100000
            }
        }

        # Sign the data
        public_key = account.public_key[2:]  # Remove '04' prefix for SECP256k1
        signature, data_hash = keystore.data_sign(
            private_key=private_key,
            msg=tx_data,
            prefix=False  # Match your Metagraph's serialization requirements
        )

        # Build the transaction with proof
        tx = {
            "value": tx_data,
            "proofs": [{
                "id": public_key,
                "signature": signature
            }]
        }

        # Submit to Metagraph
        response = await metagraph_client.network.post_data(tx)
        print("Data Transaction Response:", response)

    asyncio.run(send_data_transaction())

.. dropdown:: Data Signing Details
    :animate: fade-in

    * **Encoding and Prefix**:

      - Set ``prefix=False`` to **not** prepend ``\u0019Constellation Signed Data:\n`` to the payload.
      - Use ``encoding="base64"`` or a custom function if required by your Metagraph.

    * **Example Custom Encoder**:

    .. code-block:: python

        def custom_encoder(tx: dict) -> str:
            # Serialize to JSON with no whitespace
            encoded = json.dumps(tx, separators=(",", ":"))
            # Convert to Base64
            return base64.b64encode(encoded.encode()).decode()

        signature, hash_ = keystore.data_sign(
            private_key=private_key,
            msg=tx_data,
            encoding=custom_encoder
        )