Configuration
=============

In :doc:`DagAccount() </account/account.network>` the network is configured by calling ``DagAccount().connect(...)``.
This calls ``DagTokenNetwork().config(...)`` that validates the parameter values, sets the network variable (``self.connected_network``)
and emits an event stored in the variable ``self._network_change`` as a RxPy ``BehaviorSubject()``.

DAG Token Network
^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph import DagTokenNetwork()

    network = DagTokenNetwork(network_id="mainnet")
    network.config("testnet") # Change network

``DagTokenNetwork`` is configurable with the following parameters:

.. table::
   :widths: auto

   =================================================  ===================================================================  =============================================================
   **Parameter**                                      **Value**                                                            **Description**
   =================================================  ===================================================================  =============================================================
   network_id                                         ``"mainnet" (default)``,                                             Specify the connected network by setting this value.
                                                      ``"integrationnet"``,
                                                      ``"testnet"``
   l0_host                                            ``f"https://l0-lb-{network_id}.constellationnetwork.io" (default)``  Set a custom layer 0 API URL for ``self.connected_network``
                                                                                                                           used to configure the ``Layer0Api`` object ``self.l0_api``.
   currency_l1_host                                   ``f"https://l1-lb-{network_id}.constellationnetwork.io" (default)``  Set a custom layer 1 currency API URL for ``self.connected_network``
                                                                                                                           used to configure the ``Layer1Api`` object ``self.cl1_api``.
   block_explorer_url                                 ``f"https://be-{network_id}.constellationnetwork.io" (default)``     Set a custom block explorer API URL for ``self.connected_network``
                                                                                                                           used to configure the ``BlockExplorerApi`` object ``self.be_url``.
   :doc:`client </network/network.rest_api_clients>`  ``httpx async client (default)``                                     REST client dependency can be injected here.
   =================================================  ===================================================================  =============================================================

Metagraph Token Network
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork()

    metagraph_network = MetagraphTokenNetwork(...)

``MetagraphTokenNetwork`` is configurable with the following parameters:

.. table::
   :widths: auto

   =================================================  ================================================================  =============================================================
   **Parameter**                                      **Value**                                                         **Description**
   =================================================  ================================================================  =============================================================
   network_id                                         ``"mainnet" (default)``,                                          Specify the connected network by setting this value.
                                                      ``"integrationnet"``,
                                                      ``"testnet"``
   l0_host                                            ``None (default)``                                                Set a custom layer 0 API URL for ``self.connected_network``
                                                                                                                        used to configure the ``MetagraphLayer0Api`` object ``self.l0_api``.
   currency_l1_host                                   ``None (default)``                                                Set a custom layer 1 currency API URL for ``self.connected_network``
                                                                                                                        used to configure the ``MetagraphCurrencyLayerApi`` object ``self.cl1_api``.

   data_l1_host                                       ``None (default)``                                                Set a custom layer 1 currency API URL for ``self.connected_network``
                                                                                                                        used to configure the ``MetagraphDataLayerApi`` object ``self.dl1_api``.
   block_explorer_url                                 ``f"https://be-{network_id}.constellationnetwork.io" (default)``  Set a custom block explorer API URL for ``self.connected_network``
                                                                                                                        used to configure the ``BlockExplorerApi`` object ``self.be_url``.
   :doc:`client </network/network.rest_api_clients>`  ``httpx async client (default)``                                  REST client dependency can be injected here.
   =================================================  ================================================================  =============================================================