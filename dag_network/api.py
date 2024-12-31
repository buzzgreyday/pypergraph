from .constants import DEFAULT_L1_BASE_URL

import requests

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
        else:
            response.raise_for_status()