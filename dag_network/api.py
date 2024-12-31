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
    def handle_response(response):
        if response.status_code == 200:
            return response.json()
        # Check for a 400 error
        elif response.status_code == 400:
            # Look for the specific error message in the 'errors' list
            for error in response.json().get("errors", []):
                if "InsufficientBalance" in error.get("message", ""):
                    # Parse the amount and balance from the message
                    message = error["message"]
                    amount_str = message.split("amount=")[1].split(",")[0]
                    balance_str = message.split("balance=")[1].strip("}")

                    amount = int(amount_str)
                    balance = int(balance_str)

                    # Raise the custom exception
                    raise TransactionApiError("Insufficient balance for transaction", response.status_code)

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
        API.handle_response(response)

