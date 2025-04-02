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

Each of these classes relies on ``pypergraph.core.rest_api_client`` for performing REST operations.
By default HTTP methods are handled by ``httpx`` but dependencies can be injected using the abstract class ``pypergraph.core.api.rest_client.RESTClient()``:

.. code-block:: python


    class RestAPIClient:
        def __init__(self, base_url: str, client: Optional[RESTClient] = None, timeout: int = 10):
            """
            Initializes the RestAPIClient.

            :param base_url: The base URL for the API.
            :param client: Optional user-provided AsyncClient.
            :param timeout: Request timeout in seconds.
            """
            self.base_url = base_url.rstrip("/")
            self._external_client = client is not None
            # If no client is provided, use the default HttpxClient.
            self.client: RESTClient = client or HttpxClient(timeout=timeout)

