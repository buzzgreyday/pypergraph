Metagraph Layer 0 API
=====================

==============  ===========================================================================
**Parameters**  **Description**
==============  ===========================================================================
host            Metagraph layer 0 base url, e.g. ``https://metagraph-layer0-url.com``
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
    network.l0_api.config(host=..., client=inject_client)

-----

All Methods
-----------

Inherits from :doc:`L0Api </network/api/network.api.l0>`.

.. automodule:: pypergraph.network.api.metagraph_layer_0_api
   :members:
   :no-index:
   :undoc-members:
   :show-inheritance:
