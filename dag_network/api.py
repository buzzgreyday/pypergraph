from .constants import DEFAULT_L1_BASE_URL
import aiohttp
import asyncio


class TransactionApiError(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error = error_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (status code: {self.error})"


class API:
    @staticmethod
    async def handle_response(response):
        if response.status == 200:
            return await response.json()

        elif response.status == 400:
            response_data = await response.json()
            for error in response_data.get("errors", []):
                if "InsufficientBalance" in error.get("message", ""):
                    message = error["message"]
                    amount_str = message.split("amount=")[1].split(",")[0]
                    balance_str = message.split("balance=")[1].strip("}")

                    amount = int(amount_str)
                    balance = int(balance_str)

                    raise TransactionApiError("Insufficient balance for transaction", response.status)

    @staticmethod
    async def get_last_reference(dag_address: str):
        endpoint = f"/transactions/last-reference/{dag_address}"
        url = DEFAULT_L1_BASE_URL + endpoint

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    @staticmethod
    async def post_transaction(tx: dict):
        endpoint = "/transactions"
        url = DEFAULT_L1_BASE_URL + endpoint
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=tx) as response:
                print(await response.json())
                await API.handle_response(response)

