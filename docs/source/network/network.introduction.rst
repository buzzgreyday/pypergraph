Introduction
============

Networks can be either a ``DagTokenNetwork()`` class or a ``MetagraphTokenNetwork()`` class. These classes have methods for easing API interactions. Both are temporarily configured using the ``NetworkInfo`` class [missing ref]. The main difference between the two classes is the parameters they support.

-----

DAG Token Network
^^^^^^^^^^^^^^^^^

A network object is instantiated like this:

.. code-block:: python

    from pypergraph import DagTokenNetwork()

    network = DagTokenNetwork(network_id="mainnet")

.. table::
   :widths: auto

   =================  ===================================  =============================================================
   **Variable**       **Value**                            **Description**
   =================  ===================================  =============================================================
   connected_network  NetworkInfo()                        Class used to configure ``DagTokenNetwork`` and
                                                           ``MetagraphTokenNetwork``. See next page for supported configuration.
   _network_change    BehaviorSubject()                    RxPy BehaviorSubject that stores the emitted events.

   network_id         ``"mainnet" (default)``,             Specify the connected network by setting this value.
                      ``"integrationnet"``,
                      ``"testnet"``
   l0_api             ``Layer0Api(                         Layer 0 API class containing methods for interacting
                      host=connected_network.l0_host       with the global layer 0 API endpoints.
                      )``
   cl1_api            ``Layer1Api(                         Layer 1 API class containing methods for interacting
                      host=connected_network.l1_host       with the currency layer 1 API endpoints.
                      )``
   be_api             ``BlockExplorerApi(                  Block explorer API class containing methods for
                      host=self.connected_network.be_url   interacting with the Constellation block explorer
                      )``                                  API endpoints.
   =================  ===================================  =============================================================

RxPy Event Emitter
------------------

An event is emitted on ``DagTokenNetwork().set_network(...)`` called in ``DagTokenNetwork().config(...)``.

.. table::
   :widths: auto

   =======  ============================
   **Key**  **Value**
   =======  ============================
   module   ``"network"``
   type     ``"network_change"``
   event    ``DagTokenNetwork().get_network()``
   =======  ============================

See also the ``Monitor`` [missing link].

-----

Metagraph Token Network
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork()

    metagraph_network = MetagraphTokenNetwork(...)

.. table::
   :widths: auto

   =================  ==========================================  =======================================================
   **Variable**       **Value**                                   **Description**
   =================  ==========================================  =======================================================
   connected_network  NetworkInfo()                               Class used to configure ``DagTokenNetwork`` and
                                                                  ``MetagraphTokenNetwork``. See next page for supported
                                                                  configuration.
   network_id         ``"mainnet" (default)``,                    Specify the connected network by setting this value.
                      ``"integrationnet"``,
                      ``"testnet"``
   metagraph_id       ``None (default)``                          The DAG address used to identify the Metagraph
                                                                  (not necessary when transacting DAG).
   l0_api             ``None (default)``,                         Layer 0 API class containing methods for interacting with
                      ``MetagraphLayer0Api(                       Metagraph layer 0 API endpoints.
                      connected_network.l0_host
                      )``
   cl1_api            ``None (default)``,                         Layer 1 API class containing methods for interacting with
                      ``MetagraphCurrencyLayerApi(                Metagraph currency layer 1 API endpoints.
                      connected_network.currency_l1_host
                      )``
   dl1_api            ``None (default)``,                         Layer 1 API class containing methods for interacting with
                      ``MetagraphDataLayerApi(                    Metagraph data layer 1 API endpoints. Used for custom data.
                      connected_network.data_l1_host
                      )``
   be_api             ``None (default)``,                         Block explorer API class containing methods for interacting
                      ``BlockExplorerApi(                         with Constellation's block explorer.
                      connected_network.block_explorer_url
                      )``
   =================  ==========================================  =======================================================
