Network
=======

This section documents how to switch network and connect to Metagraphs.

-----

.. code-block:: python

    from pypergraph import DagAccount()

    account = DagAccount().connect(...)


.. table::
   :widths: auto

   ==================  ===================================================================  =============
   Parameter           Value                                                                Description
   ==================  ===================================================================  =============
   network_id          ``"mainnet" (default)``, ``"integrationnet"``, ``"testnet"``         Specify the connected network by setting this value.
   metagraph_id        ``None (default)``                                                   The DAG address used to identify the Metagraph
                                                                                            (not necessary when transacting DAG).
   l0_host             ``f"https://l0-lb-{network_id}.constellationnetwork.io" (default)``  Specify a particular global layer 0 host (e.g. IP and port)
   currency_l1_host    ``f"https://l1-lb-{network_id}.constellationnetwork.io" (default)``  Specify a particular currency layer 1 host (e.g. IP and port)
   data_l1_host        ``None (default)``                                                   Specify a particular data layer 1 host (e.g. IP and port).
                                                                                            Used for custom data transactions (not currency transaction).
   block_explorer_url  ``f"https://be-{network_id}.constellationnetwork.io" (default)``     The block explorer URL can be changed.
   ==================  ===================================================================  =============

See :doc:`network documentation </network/network.introduction>` for more detail.

-----

Switch DAG Network
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_account import DagAccount

    # Initialize the DAG account and log in using a seed phrase.
    account = DagAccount()
    account.login_with_seed_phrase("abandon abandon ...")

    # Connect to the specified network (e.g., testnet).
    account.connect(network_id="testnet")

-----

Connect to Metagraph
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Create a Metagraph token client with custom node configurations.
    metagraph_client = account.create_metagraph_token_client(
        metagraph_id="DAG7...",
        l0_host="http://custom-l0-node:9100",
        cl1_host="http://custom-cl1-node:9200",
        dl1_host="http://custom-dl1-node:9300"
    )

.. dropdown:: Alternative Method
    :animate: fade-in

    .. code-block:: python

        from pypergraph.account import MetagraphTokenClient

        # Alternative method to create a Metagraph token client.
        metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7...",
            l0_host="http://custom-l0-node:9100",
            cl1_host="http://custom-cl1-node:9200",
            dl1_host="http://custom-dl1-node:9300"
        )
