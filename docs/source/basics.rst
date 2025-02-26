Basics
======

Account/Wallet
______________

In Pypergraph wallets are referred to as accounts.

* **CREATE DAG ACCOUNT FROM EXISTING SECRET**

.. code-block:: python

    seed_phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
    account = pypergraph.dag-account.DagAccount()
    account.login_with_seed_phrase(words=seed_phrase)

.. code-block:: python

    private_key = "this01is02A03Fake04PRIVATE05key06"
    account = pypergraph.dag-account.DagAccount()
    account.login_with_private_key(private_key=private_key)

* **SEND TRANSACTION**

    First create an account and login using a seed or private key. Then generate a new signed transaction specifying the receiving DAG address, the amount to send, the fee (both with 8 decimals) and optionally the account's last transaction hash reference. In the example below `1` $DAG is sent with a fee of `0.002` $DAG to `DAG2this01is02A03FAKE04DAG05Address06`.

.. code-block:: python

    # Create an account and login
    seed_phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
    account = pypergraph.dag-account.DagAccount()
    account.login_with_seed_phrase(words=seed_phrase)
    # Generate signed transaction
    tx, hash_ = await account.generate_signed_transaction(to_address="DAG2this01is02A03FAKE04DAG05Address06", amount=100000000, fee=200000)
    # Send transaction
    await account.network.post_transaction(tx)

.. code-block:: python

    # Create an account and login
    seed_phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
    account = pypergraph.dag-account.DagAccount()
    account.login_with_seed_phrase(words=seed_phrase)
    # Change network to "testnet", "integrationnet" or "mainnet"
    account.connect(network_id="testnet")
    # Generate signed transaction
    tx, hash_ = await account.generate_signed_transaction(to_address="DAG2this01is02A03FAKE04DAG05Address06", amount=100000000, fee=200000)
    # Send transaction
    await account.network.post_transaction(tx)

.. code-block:: python

    # Create account and login
    seed_phrase = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
    account = pypergraph.dag_account.DagAccount()
    account.login_with_seed_phrase(words=seed_phrase)
    # Create a Metagraph client to interact with Metagraphs
    account_metagraph_client = pypergraph.dag_account.MetagraphTokenClient(account=account, metagraph_id="DAG7ChnhUF7uKgn8tXy45aj4zn9AFuhaZr8VXY43", l0_host="http://elpaca-l0-2006678808.us-west-1.elb.amazonaws.com:9100", cl1_host="http://elpaca-cl1-1512652691.us-west-1.elb.amazonaws.com:9200")
    last_ref = await account_metagraph_client.network.get_address_last_accepted_transaction_ref(address=from_address)
    tx, hash_ = await account_metagraph_client.account.generate_signed_transaction(to_address=to_address, amount=100000000, fee=0, last_ref=last_ref)
    # Send transaction
    await account_metagraph_client.network.post_transaction(tx=tx.model_dump()) # This model dump situation should be handled

.. dropdown:: Variations
    :animate: fade-in

    .. code-block:: python

        Placeholder

-----

* **LOGIN OPTIONS**

    After creating the account object you can login and start interacting with the Constellation APIs.

1. Login with seed phrase:

.. code-block:: python

        account.login_with_seed_phrase("abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon")

2. Login with private key:

.. code-block:: python

        account.login_with_private_key("your_private_key_here")

3. Login with public key (private key is needed to send transactions, etc.):

.. code-block:: python

        account.login_with_public_key("your_public_key_here")

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

    wallet = Account.from_private_key("SOME_VALID_PRIVATE_KEY")

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

  Reconfigures the ``wallet.network`` object variable used to handle interaction with Constellation APIs. The parameters ``l0_host`` and ``l1_host`` with "http//" or "https://" prefix is required if ``metagraph_id`` is set.

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
