import aiohttp


class TransactionApiError(Exception):
    def __init__(self, message, error_code):
        self.message = message
        self.error = error_code
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (status code: {self.error})"


class API:

    def __init__(self, network: str = "mainnet", layer: int = 1):
        self.network = network
        self.layer = layer
        self.current_base_url = f"https://l{self.layer}-lb-{self.network}.constellationnetwork.io"
        self.current_block_explorer_url = f"https://be-{self.network}.constellationnetwork.io"

    def __repr__(self):
        return f"API(network={self.network}, layer={self.layer}, current_base_url={self.current_base_url}"

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

    async def get_address_balance(self, hash: str):
        """
        :param hash: DAG address or public key
        :return: dictionary
        """
        endpoint = f"/addresses/${hash}/balance"
        url = self.current_block_explorer_url + endpoint

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    async def get_last_reference(self, hash: str):
        endpoint = f"/transactions/last-reference/{hash}"
        url = self.current_base_url + endpoint

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    async def get_pending_transaction(self, hash: str):
        endpoint = f"/transactions/{hash}"
        url = self.current_base_url + endpoint
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

    async def post_transaction(self, tx: dict):
        endpoint = "/transactions"
        url = self.current_base_url + endpoint
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=tx) as response:
                print(await response.json())
                await API.handle_response(response)

