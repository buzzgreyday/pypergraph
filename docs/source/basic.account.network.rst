Account Network
===============

.. admonition:: Network Configurations

    The connected network can be configured with the following parameters:

    - :code:`network_id = "mainnet"` (default), :code:`"integrationnet"` or :code:`"testnet"`. Only setting this value will set the parameters below to the default values.

    - :code:`metagraph_id = None` (default). Used to identify the connected Metagraph.
    - :code:`l0_host = f"https://l0-lb-{network_id}.constellationnetwork.io"` (default). Global layer 0 URL (e.g. :code:`"http://123.123.123.123:9000"`)
    - :code:`cl1_host = f"https://l1-lb-{network_id}.constellationnetwork.io"` (default). Currency layer 1 URL (e.g. :code:`"http://123.123.123.123:9010"`)
    - :code:`dl1_host = None` (default). Data layer 1 URL (e.g. :code:`"http://123.123.123.123:9020"`) used with Metagraphs.
    - :code:`l0_lb_url = f"https://l0-lb-{network_id}.constellationnetwork.io"` (default). Layer 0 load balancer is not used with Metagraphs.
    - :code:`l1_lb_url = f"https://l1-lb-{network_id}.constellationnetwork.io"` (default). Layer 1 load balancer is not used with Metagraphs.
    - :code:`be_url = f"https://be-{network_id}.constellationnetwork.io"` (default).

Switch DAG Network
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph.dag_account import DagAccount

    account = DagAccount()
    account.login_with_seed_phrase("abandon abandon ...")
    account.connect(network_id="testnet")

Connect to Metagraph
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

        metagraph_client = account.create_metagraph_token_client(
            metagraph_id="DAG7...",
            l0_host="http://custom-l0-node:9100",
            cl1_host="http://custom-cl1-node:9200",
            dl1_host="http://custom-dl1-node:9300"
        )

.. dropdown:: Alternative
    :animate: fade-in

    .. code-block:: python

        from pypergraph.account import MetagraphTokenClient

        metagraph_client = MetagraphTokenClient(
            account=account,
            metagraph_id="DAG7...",
            l0_host="http://custom-l0-node:9100",
            cl1_host="http://custom-cl1-node:9200",
            dl1_host="http://custom-cl1-node:9300"
        )