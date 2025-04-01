Configuration
=============

In :doc:`DagAccount() </account/account.network>` the network is configured by calling ``DagAccount().connect(...)``.
This calls ``DagTokenNetwork().config(...)`` that validates the parameter values, sets the network variable (``self.connected_network``)
and emits an event stored in the variable ``self._network_change`` as a RxPy ``BehaviorSubject()``.

DAG Token Network
^^^^^^^^^^^^^^^^^

``DagTokenNetwork`` is configurable with the following parameters:

.. table::
   :widths: auto

   ==================  =============================================  =============================================================
   **Parameter**       **Value**                                      **Description**
   ==================  =============================================  =============================================================
   network_id          ``"mainnet" (default)``,                       Specify the connected network by setting this value.
                       ``"integrationnet"``,
                       ``"testnet"``
   l0_host             ``self.connected_network.l0_host``             Set a custom layer 0 API URL for ``self.connected_network``
                                                                      used to configure the ``MetagraphLayer0Api`` object ``self.l0_api``.
   currency_l1_host    ``self.connected_network.currency_l1_host``    Set a custom layer 1 currency API URL for ``self.connected_network``
                                                                      used to configure the ``MetagraphCurrencyLayerApi`` object ``self.cl1_api``.
   data_l1_host        ``self.connected_network.data_l1_host``        Set a custom layer 1 data API URL for ``self.connected_network``
                                                                      used to configure the ``MetagraphDataLayerApi`` object ``self.dl1_api``.
   block_explorer_url  ``self.connected_network.block_explorer_url``  Set a custom block explorer API URL for ``self.connected_network``
                                                                      used to configure the ``BlockExplorerApi`` object ``self.be_url``.
   ==================  =============================================  =============================================================

Metagraph Token Network
^^^^^^^^^^^^^^^^^^^^^^^

``MetagraphTokenNetwork`` is configurable with the following parameters:

.. table::
   :widths: auto

   ==================  =============================================  =============================================================
   **Parameter**       **Value**                                      **Description**
   ==================  =============================================  =============================================================
   network_id          ``"mainnet" (default)``,                       Specify the connected network by setting this value.
                       ``"integrationnet"``,
                       ``"testnet"``
   l0_host             ``self.connected_network.l0_host``             Set a custom layer 0 API URL for ``self.connected_network``
                                                                      used to configure the ``Layer0Api`` object ``self.l0_api``.
   currency_l1_host    ``self.connected_network.currency_l1_host``    Set a custom layer 1 currency API URL for ``self.connected_network``
                                                                      used to configure the ``Layer1Api`` object ``self.cl1_api``.
   data_l1_host        ``self.connected_network.data_l1_host``
   block_explorer_url  ``self.connected_network.block_explorer_url``  Set a custom block explorer API URL for ``self.connected_network``
                                                                      used to configure the ``BlockExplorerApi`` object ``self.be_url``.
   ==================  =============================================  =============================================================