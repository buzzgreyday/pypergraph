Block Explorer API
==================

==============  ===========================================================================
**Parameters**  **Description**
==============  ===========================================================================
host            Block explorer base url, e.g. ``http://be-mainnet.constellationnetwork.io``
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
    network.be_api.config(host=..., client=inject_client)

-----

All Methods
-----------

.. automodule:: pypergraph.network.api.block_explorer_api
   :members:
   :no-index:
   :undoc-members:
   :show-inheritance:


