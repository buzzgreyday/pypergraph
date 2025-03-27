Introduction
============

Networks can be either a ``DagTokenNetwork()`` class or a ``MetagraphTokenNetwork()`` class. These classes have methods for easing API interactions. Both are temporarily configured using the ``NetworkInfo`` class [missing ref]. The main difference between the two classes is the parameters they support.

-----

DAG Token Network
-----------------

A network object is instantiated like this:

.. code-block:: python

    from pypergraph import DagTokenNetwork()

    network = DagTokenNetwork(...)

.. table::
   :widths: auto

   =================  =================  =============================================================
   Variable           Value              Description
   =================  =================  =============================================================
   connected_network  NetworkInfo()      Python class used to configure ``DagTokenNetwork`` and
                                         ``MetagraphTokenNetwork``. See below for supported configuration.
   _network_change    BehaviorSubject()  RxPy BehaviorSubject that stores the emitted events.
   =================  =================  =============================================================

Additional properties of ``DagTokenNetwork`` and ``NetworkInfo``:

.. code-block:: python

   l0_api = Layer0Api(host=self.connected_network.l0_host)

.. table::
   :widths: auto

   ============  ===================================================================  ===========================================================
   Variable      Value                                                                Description
   ============  ===================================================================  ===========================================================
   network_id    ``"mainnet" (default)``, ``"integrationnet"``, ``"testnet"``         Specify the connected network by setting this value.
   l0_api        ``Layer0Api(host=connected_network.l0_host)``                        Layer 0 API class containing methods for interacting
                                                                                      with the global layer 0 API endpoints.
   cl1_api       ``Layer1Api(host=connected_network.l1_host)``                        Layer 1 API class containing methods for interacting
                                                                                      with the currency layer 1 API endpoints.
   be_api        ``BlockExplorerApi(host=self.connected_network.be_url)``             Block explorer API class containing methods for
                                                                                      interacting with the Constellation block explorer
                                                                                      API endpoints.
   ============  ===================================================================  ===========================================================

-----

Metagraph Token Network
-----------------------

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork()

    metagraph_network = MetagraphTokenNetwork(...)

.. table::
   :widths: auto

   =================  ==============  ===============================================
   Variable           Value           Description
   =================  ==============  ===============================================
   connected_network  NetworkInfo()   Python class used to configure ``DagTokenNetwork`` and
                                      ``MetagraphTokenNetwork``. See below for supported configuration.
   =================  ==============  ===============================================

Properties shared by ``DagMetagraphNetwork`` and ``NetworkInfo``:

.. table::
   :widths: auto

   ============  ========================================================================================  ===========================================================
   Variable      Value                                                                                     Description
   ============  ========================================================================================  ===========================================================
   network_id    ``"mainnet" (default)``, ``"integrationnet"``, ``"testnet"``                              Specify the connected network by setting this value.
   metagraph_id  ``None (default)``                                                                        The DAG address used to identify the Metagraph
                                                                                                           (not necessary when transacting DAG).
   l0_api        ``MetagraphLayer0Api(connected_network.l0_host)`` or not set (default)                    Layer 0 API class containing methods for interacting with
                                                                                                           Metagraph layer 0 API endpoints.
   cl1_api       ``MetagraphCurrencyLayerApi(connected_network.currency_l1_host)`` or not set (default)    Layer 1 API class containing methods for interacting with
                                                                                                           Metagraph currency layer 1 API endpoints.
   dl1_api       ``MetagraphDataLayerApi(connected_network.data_l1_host)`` or not set (default)            Layer 1 API class containing methods for interacting with
                                                                                                           Metagraph data layer 1 API endpoints. Used for custom data.
   be_api        ``BlockExplorerApi(connected_network.block_explorer_url)`` or not set (default)           Block explorer API class containing methods for interacting
                                                                                                           with Constellation's block explorer.
   ============  ========================================================================================  ===========================================================
