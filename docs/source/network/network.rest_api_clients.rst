REST API Clients
================

Pypergraph relies on 6 REST API classes:

======================================================  ===============================
**Class**                                               **Description**
======================================================  ===============================
:doc:`BlockExplorerApi </network/api/network.api.be>`   Methods for block explorer operations.
:doc:`L0Api </network/api/network.api.l0>`              Methods for layer 0 operations.
:doc:`L1Api </network/api/network.api.l1>`              Methods for layer 1 currency operations.
:doc:`ML0Api </network/api/network.api.ml0>`            Methods for layer 0 Metagraph operations.
:doc:`ML1Api </network/api/network.api.ml1>`            Methods for layer 1 Metagraph currency operations.
:doc:`MDL1Api </network/api/network.api.mdl1>`          Methods for layer 1 Metagraph data operations.
======================================================  ===============================

-----

Inject Non-Default Client
-------------------------

Each of the classes above rely on ``pypergraph.core.rest_api_client.RestAPIClient(...)`` for performing REST operations.
By default HTTP methods are handled by ``httpx`` but dependency injection is possible by inheriting from the abstract
class ``pypergraph.core.cross_platform.api.rest_client.RESTClient()``:

.. code-block:: python

    from pypergraph import DagTokenNetwork
    from pypergraph.core.cross_platform.di.rest_client import RESTClient

    class HttpxClient(RESTClient):
        def __init__(self, timeout: int = 10):
            self.client = httpx.AsyncClient(timeout=timeout)

        async def request(
            self,
            method: str,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            payload: Optional[Dict[str, Any]] = None,
        ) -> Response:
            return await self.client.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=payload
            )

        async def close(self):
            await self.client.aclose()

    network = DagTokenNetwork(..., client=HttpxClient())
