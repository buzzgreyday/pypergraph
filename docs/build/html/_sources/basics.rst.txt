Account Management
==================

Wallet Creation
---------------

.. admonition:: Cryptographic Key Trio

    Constellation Network accounts utilize a cryptographic key trio comprising:

    - **Private Key**: A secure cryptographic element used to authenticate ownership and authorize transactions.
      Required for signing transactions and messages. **Treat as sensitive information**.
    - **Public Key**: Derived from the private key, serves as a network identifier for node authentication and
      signature verification in trust relationships.
    - **Address**: Public wallet identifier generated from cryptographic keys. Shareable for receiving transactions
      while maintaining private key confidentiality.

-----

New Wallet Generation
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_keystore import KeyStore
    from pypergraph.dag_account import DagAccount

    keystore = KeyStore()
    mnemonic = keystore.get_mnemonic()  # Generate BIP-39 compliant seed phrase

    # Initialize account after securing mnemonic
    account = DagAccount()
    account.login_with_seed_phrase(words=mnemonic)

    print(f"Generated Address: {account.address}")


Existing Credential Authentication
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_account import DagAccount

    account = DagAccount()
    account.login_with_seed_phrase(words="abandon abandon ...")  # Provide 12-word mnemonic

.. dropdown:: Authentication Methods
    :animate: fade-in-slide-down

    **Mnemonic Authentication**
    .. code-block:: python

        account.login_with_seed_phrase("abandon abandon ...")

    **Private Key Authentication**
    .. code-block:: python

        account.login_with_private_key("private_key_here")

    **Public Key Authentication** (Read-only)
    .. note::
        Transaction submission requires private key access
    .. code-block:: python

        account.login_with_public_key("public_key_here")

-----

Transaction Operations
----------------------

Standard DAG Transfer
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_account import DagAccount
    import asyncio

    async def execute_transfer():
        account = DagAccount()
        account.login_with_seed_phrase("abandon abandon ...")
        account.connect(network_id="testnet")  # Default: mainnet

        transaction_hash = await account.transfer(
            to_address="DAG1...",
            amount=100000000,  # 1 DAG = 10^8 units
            fee=200000
        )
        print(f"Transaction ID: {transaction_hash}")

    asyncio.run(execute_transfer())

Advanced Transaction Construction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. dropdown:: Transaction Lifecycle Management
    :animate: fade-in

    .. code-block:: python

        # Transaction preparation
        tx, tx_hash = await account.generate_signed_transaction(
            to_address="DAG1...",
            amount=100000000,
            fee=200000,
            last_ref=await account.network.get_address_last_accepted_transaction_ref(account.address)
        )

        # Network submission
        await account.network.post_transaction(tx)

.. dropdown:: Network Configuration
    :animate: fade-in

    Configure connection parameters via ``account.connect()``:

    - **Network Presets**:
        - ``network_id="mainnet"`` (default)
        - ``network_id="testnet"``
        - ``network_id="integrationnet"``
    - **Endpoint Overrides**:
        - ``be_url``: Blockchain Explorer URL
        - ``l0_url``: Layer 0 API endpoint
        - ``cl1_url``: Currency Layer 1 endpoint

Metagraph Token Transactions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_account import MetagraphTokenClient

    async def metagraph_transfer():
        account = DagAccount().login_with_seed_phrase("abandon ...")

        metagraph = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7...",
            l0_host="http://custom-l0-node:9100",
            cl1_host="http://custom-cl1-node:9200"
        )

        tx_hash = await metagraph.transfer(
            to_address="DAG2recipient...",
            amount=100000000,
            fee=0  # Metagraph-specific fee rules
        )

Bulk Transaction Processing
^^^^^^^^^^^^^^^^^^^^^^^^^^^

DAG Bulk Currency Transfers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def batch_transfers():
        account = DagAccount().login_with_seed_phrase("abandon ...")
        transfers = [
            {"to_address": "DAG1...", "amount": 100000000},
            {"to_address": "DAG1...", "amount": 50000000, "fee": 200000}
        ]
        tx_hashes = await account.transfer_dag_batch(transfers=transfers)

Metagraph Bulk Currency Transfers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    async def metagraph_batch():
        metagraph = MetagraphTokenClient(...)
        transfers = [
            {"to_address": "DAG2...", "amount": 100000000},
            {"to_address": "DAG2...", "amount": 50000000, "fee": 200000}
        ]
        tx_hashes = await metagraph.transfer_batch(transfers=transfers)

Data Transaction Submission
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_keystore import KeyStore

    async def submit_metagraph_data():
        account = DagAccount().login_with_seed_phrase("abandon ...")
        metagraph = MetagraphTokenClient(..., dl1_host="http://custom-dl1-node:9300")

        payload = {
            "CreatePoll": {
                "name": "consensus_vote",
                "owner": account.address,
                "pollOptions": ["approve", "reject"],
                "startSnapshotOrdinal": 1000,
                "endSnapshotOrdinal": 100000
            }
        }

        signature, data_hash = KeyStore().data_sign(
            private_key=account.private_key,
            msg=payload,
            prefix=False
        )

        response = await metagraph.network.post_data({
            "value": payload,
            "proofs": [{"id": account.public_key[2:], "signature": signature}]
        })

.. dropdown:: Data Signing Configuration
    :animate: fade-in

    **Serialization Options**:

    - ``prefix=False``: Exclude default data preamble
    - ``encoding='hex'``: (Default) or 'base64' or custom encoding functions, e.g.:

    .. code-block:: python

        def base64_serializer(data: dict) -> str:
            import base64, json
            return base64.b64encode(
                json.dumps(data, separators=(",", ":")).encode()
            ).decode()