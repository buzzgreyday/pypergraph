Metagraph Token Network
=======================

-----

Get Network Info
----------------

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork

    network = MetagraphTokenNetwork()
    network_info_dict = await network.get_network()

.. dropdown:: Lifecycle
    :animate: fade-in

    .. code-block:: python

        def get_network(self) -> Dict:
            return self.connected_network.__dict__

-----

Get Address Balance
-------------------

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork

    network = MetagraphTokenNetwork()
    balance = await network.get_address_balance("DAG1...")

.. dropdown:: Lifecycle
    :animate: fade-in

    .. code-block:: python

        async def get_address_balance(self, address: str) -> Balance:
            return await self.l0_api.get_address_balance(address)

-----

Get Last Accepted Transaction Reference per Address
---------------------------------------------------

When building a new transaction a hash reference to the previous transaction made by the account is used to chain the transactions together.

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork

    network = MetagraphTokenNetwork()

    last_ref = await network.get_address_last_accepted_transaction_ref("DAG1...")

    tx_hash = last_ref.hash
    ordinal = last_ref.ordinal

.. dropdown:: Lifecycle
    :animate: fade-in

    .. code-block:: python

        async def get_address_last_accepted_transaction_ref(self, address: str) -> TransactionReference:
            return await self.cl1_api.get_last_reference(address)

-----

Get Pending Transaction
-----------------------

Check if a transaction is pending. Returns ``None`` and logs result, if transaction is not pending.

.. code-block:: python

    import asyncio

    from pypergraph import MetagraphTokenNetwork

    network = MetagraphTokenNetwork()

    for _ in range(0, 5):
        pending_tx = await network.get_pending_transaction("f123...") # Transaction hash
        if pending_tx:
            break
        await asyncio.sleep(10)

.. dropdown:: Lifecycle
    :animate: fade-in

    .. code-block:: python

        async def get_pending_transaction(self, hash: str) -> PendingTransaction:
            try:
                return await self.cl1_api.get_pending_transaction(hash)
            except NetworkError as e:
                # NOOP for 404 or other exceptions
                if e.status == 404:
                    logger.debug("No transaction pending.")
                else:
                    logger.error(f"{e}")
                    raise e

-----

Get Transactions for Address
----------------------------

Get all transaction by address (supports pagination). Returns ``None`` and logs result, if no transactions are found.

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork

    network = MetagraphTokenNetwork()

    txs = await network.get_transactions_by_address("DAG1...", 10)

.. dropdown:: Lifecycle
    :animate: fade-in

    .. code-block:: python

        async def get_transactions_by_address(
            self,
            address: str,
            limit: Optional[int] = None, # Results per page
            search_after: Optional[str] = None, # Timestamp
        ) -> List[Transaction]:
            try:
                return await self.be_api.get_transactions_by_address(address, limit, search_after)
            except Exception:
                # NOOP for 404 or other exceptions
                logger.info(f"No transactions found for {address}.")

-----

Get Accepted Transaction
------------------------

Returns ``None`` and logs the result, if no transaction is found.

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork

    network = MetagraphTokenNetwork()

    tx = await network.get_transaction("f123...")

.. dropdown:: Lifecycle
    :animate: fade-in

    .. code-block:: python

        async def get_transaction(self, hash: str) -> Transaction:
            try:
                return await self.be_api.get_transaction(hash)
            except Exception:
                # NOOP for 404 or other exceptions
                logger.info("MetagraphTokenNetwork :: No transaction found.")

-----

Post Signed Transaction
-----------------------

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork

    network = MetagraphTokenNetwork()

    tx_hash = await network.post_transaction(tx)

.. dropdown:: Lifecycle
    :animate: fade-in

    .. code-block:: python

        async def post_transaction(self, tx: SignedTransaction) -> str:
            try:
                response = await self.cl1_api.post_transaction(tx)
                # Support data/meta format and object return format
                return response["data"]["hash"] if "data" in response else response["hash"]
            except AttributeError:
                logging.warning("MetagraphTokenNetwork :: Currency layer 1 API object not set.")

-----

Post Signed Data
----------------

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork

    network = MetagraphTokenNetwork()

    response = await network.post_data(tx)

.. dropdown:: Lifecycle
    :animate: fade-in

    .. code-block:: python

        async def post_data(self, tx: Dict[str, Dict]) -> dict:
            try:
                response = await self.dl1_api.post_data(tx)
                return response
            except AttributeError:
                logging.warning("MetagraphTokenNetwork :: Data layer 1 API object not set.")