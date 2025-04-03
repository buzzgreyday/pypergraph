Layer 1 Currency API
====================

==============  ===========================================================================
**Parameters**  **Description**
==============  ===========================================================================
host            Layer 1 currency base url, e.g. ``http://l1-lb-mainnet.constellationnetwork.io``
client          Non-default REST client injection of type ``RESTClient``,
                see ``pypergraph.core.cross_platform.api.rest_client``.
==============  ===========================================================================

-----

Reconfigure Client and Host
---------------------------

.. code-block:: python

    from pypergraph import DagTokenNetwork
    from pypergraph.core.cross_platform.di.RESTClient

    class InjectClient(RESTClient)
        ...

    inject_client = InjectClient()

    network = DagTokenNetwork(...)
    network.cl1_api.config(host=..., client=inject_client)

-----

All Methods
-----------

.. automodule:: pypergraph.network.api.layer_1_api
   :members:
   :no-index:
   :undoc-members:
   :show-inheritance:

