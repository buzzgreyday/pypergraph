Metagraph Layer 1 Currency API
==============================

==============  ===========================================================================
**Parameters**  **Description**
==============  ===========================================================================
host            Metagraph layer 1 currency base url, e.g. ``https://metagraph-currency-url.com``
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
    network.cl1_api.config(host=..., client=inject_client)

-----

All Methods
-----------

Inherits from :doc:`L1Api </network/api/network.api.l1>`.

.. automodule:: pypergraph.network.api.metagraph_currency_layer_1_api
   :members:
   :no-index:
   :undoc-members:
   :show-inheritance:
