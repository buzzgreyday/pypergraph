from .constants import DEFAULT_L1_BASE_URL

import requests

class TransactionApiError(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error = error_code
        super().__init__(self.message)


    def __str__(self):
        return f"{self.message} (status code: {self.error})"


class API:
    @staticmethod
    def get_last_reference(dag_address: str):

        endpoint = f"/transactions/last-reference/{dag_address}"
        url = DEFAULT_L1_BASE_URL + endpoint
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @staticmethod
    def post_transaction(tx: dict):

        endpoint = f"/transactions"
        url = DEFAULT_L1_BASE_URL + endpoint
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        # Make the POST request
        response = requests.post(url, headers=headers, json=tx)
        if response.status_code == 200:
            return response.json()
        elif response.status_code in (400, 500):
            print(response.json())
            raise TransactionApiError("Error processing request", response.status_code)
        else:
            return response.json()