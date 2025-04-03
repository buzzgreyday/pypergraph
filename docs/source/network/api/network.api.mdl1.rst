Metagraph Layer 1 Data API
==========================

==============  ===========================================================================
**Parameters**  **Description**
==============  ===========================================================================
host            Metagraph layer 1 data base url, e.g. ``https://metagraph-data-url.com``
client          Non-default REST client injection of type ``RESTClient``,
                see ``pypergraph.core.cross_platform.api.rest_client``.
==============  ===========================================================================

-----

Reconfigure Client and Host
---------------------------

.. code-block:: python

    from pypergraph import MetagraphTokenNetwork
    from pypergraph.core.cross_platform.di.RESTClient

    class InjectClient(RESTClient)
        ...

    inject_client = InjectClient()

    network = MetagraphTokenNetwork(...)
    network.dl1_api.config(host=..., client=inject_client)

-----

All Methods
-----------

.. automodule:: pypergraph.network.api.metagraph_data_layer_1_api
   :members:
   :no-index:
   :undoc-members:
   :show-inheritance:

