Transactions
============

Official Tessellation documentation on `transaction types <https://docs.constellationnetwork.io/network-fundamentals/tokens/transaction-types>`_.

-----

Single $DAG Transaction
^^^^^^^^^^^^^^^^^^^^^^^
.. note::
    :code:`Amount` and :code:`fee` are 8-decimal integers (dDAG), i.e. 1 DAG equals 100000000 dDAG.

.. code-block:: python

    from pypergraph.dag_account import DagAccount
    import asyncio

    async def execute_transfer():
        # Initialize the account and log in using a seed phrase.
        account = DagAccount()
        account.login_with_seed_phrase("abandon abandon ...")

        # Initiate a transfer which returns a pending transaction.
        pending_transaction = await account.transfer(
            to_address="DAG1...",
            amount=100000000,  # 1 DAG = 10^8 units
            fee=200000
        )
        print(f"Transaction ID: {pending_transaction.hash}")

    # Execute the async transfer function.
    asyncio.run(execute_transfer())

.. dropdown:: Transaction Creation Lifecycle
    :animate: fade-in

    .. code-block:: python

        # Transaction preparation: generate and sign a transaction.
        tx, tx_hash = await account.generate_signed_transaction(
            to_address="DAG1...",
            amount=100000000,
            fee=20000,
            last_ref=await account.network.get_address_last_accepted_transaction_ref(account.address)
        )

        # Network submission: post the transaction to the network.
        await account.network.post_transaction(tx)

-----

Batch $DAG Transactions
^^^^^^^^^^^^^^^^^^^^^^^
.. note::
    :code:`Amount` and :code:`fee` are 8-decimal integers (dDAG), i.e. 1 DAG equals 100000000 dDAG.

.. code-block:: python

    async def batch_transfers():
        # Log in using a seed phrase.
        account = DagAccount().login_with_seed_phrase("abandon abandon ...")

        # Define multiple transfers in a batch.
        transfers = [
            {"to_address": "DAG1...", "amount": 100000000},
            {"to_address": "DAG2...", "amount": 50000000, "fee": 200000}
        ]
        # Execute the batch transfer.
        tx_hashes = await account.transfer_batch(transfers=transfers)

-----

Metagraph Token
^^^^^^^^^^^^^^^
.. note::
    :code:`Amount` and :code:`fee` are 8-decimal integers (dDAG), i.e. 1 token equals 100000000 units.

.. code-block:: python

    from pypergraph.dag_account import MetagraphTokenClient
    import asyncio

    async def metagraph_transfer():
        # Log in using a seed phrase.
        account = DagAccount().login_with_seed_phrase("abandon ...")

        # Create a Metagraph token client with custom node configurations.
        metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7...",
            l0_host="http://custom-l0-node:9100",
            cl1_host="http://custom-cl1-node:9200"
        )

        # Initiate a metagraph transfer.
        tx_hash = await metagraph_client.transfer(
            to_address="DAG9...",
            amount=100000000,
            fee=0  # Metagraph-specific fee rules
        )

.. dropdown:: Alternative Metagraph Client Creation
    :animate: fade-in

    .. code-block:: python

        # Alternative method to create a Metagraph token client.
        metagraph_client = account.create_metagraph_token_client(
            metagraph_id="DAG7...",
            # Additional configuration parameters as needed.
            dl1_host="http://custom-cl1-node:9200"
        )

-----

Metagraph Data
^^^^^^^^^^^^^^
Transaction values, serialization and encoding should match what is expected by the Metagraph.

.. code-block:: python

    from pypergraph.dag_keystore import KeyStore
    import asyncio

    async def submit_metagraph_data():
        # Log in using a seed phrase.
        account = DagAccount().login_with_seed_phrase("abandon ...")

        # Create a Metagraph token client (alternative method).
        metagraph_client = account.create_metagraph_token_client(
            metagraph_id="DAG7...",
            # Additional configuration parameters as needed.
            dl1_host="http://custom-dl1-node:9300"
        )

        # Define the payload for the Metagraph data submission.
        payload = {
            "CreatePoll": {
                "name": "consensus_vote",
                "owner": account.address,
                "pollOptions": ["approve", "reject"],
                "startSnapshotOrdinal": 1000,
                "endSnapshotOrdinal": 100000
            }
        }

        # Sign the payload.
        signature, data_hash = KeyStore().data_sign(
            private_key=account.private_key,
            msg=payload
        )

        # Post the signed data to the network.
        response = await metagraph_client.network.post_data({
            "value": payload,
            "proofs": [
                {
                    "id": account.public_key[2:],  # Compressed public key (remove "04" prefix)
                    "signature": signature
                }
            ]
        })

.. dropdown:: Data Signing Configuration
    :animate: fade-in

    .. admonition:: Serialization Options

        - ``prefix=True`` (default) or ``False`` to exclude the default data preamble.
        - ``encoding=None`` (default) or e.g., ``"base64"`` or a custom encoding function.

    .. code-block:: python

        def base64_serializer(data: dict) -> str:
            import base64, json
            return base64.b64encode(
                json.dumps(data, separators=(",", ":")).encode()
            ).decode()

        # Sign the payload with custom serialization settings.
        signature, data_hash = KeyStore().data_sign(
            private_key=account.private_key,
            msg=payload,
            prefix=False,
            encoding=base64_serializer
        )
