from dag_network import RestApi
from dag_network import TransactionReference

class NetworkApi:
    def __init__(self, base_url: str):
        """
        Initialize with a single base URL, instead of a dictionary of base URLs.
        """
        self.service = RestApi(base_url)  # Use a single service instead of a dictionary of services
        self.current_service_key = base_url  # Only one service is used
        self.config = self.service.config  # Direct access to the configuration

    # dag4.dag-network.src.api.v2.l1-api.ts
    def get_address_last_accepted_transaction_ref(self, address) -> TransactionReference:
        """
        Fetch the transaction reference and parse it into a TransactionReference object.
        """
        endpoint = f"/transactions/last-reference/{address}"
        response_data = self.service.get(endpoint)  # Directly use the service instance
        print(response_data)
        return TransactionReference(**response_data)  # Parse the response into a TransactionReference