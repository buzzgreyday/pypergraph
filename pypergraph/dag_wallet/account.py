import asyncio
import time

from pypergraph.dag_keystore import KeyStore, Bip39, Bip32
from pypergraph.dag_network.network import DagTokenNetwork, MetagraphTokenNetwork

from decimal import Decimal
from pyee.asyncio import AsyncIOEventEmitter
from typing import Optional, List, Dict, Any

DAG_DECIMALS = Decimal('100000000')  # Assuming DAG uses 8 decimals


class DagAccount(AsyncIOEventEmitter):
    def __init__(self, network = None):
        super().__init__()
        self.network = network or DagTokenNetwork()
        self.key_trio = None

    def connect(self, network_info: dict):
        """
        Initiate or change connection.

        :param network_info: {"network_id": "integrationnet", "be_url": "https://be-integrationnet.constellationnetwork.io", "l0_host": None, "cl1_host": None, "l0_lb_url": "https://l0-lb-integrationnet.constellationnetwork.io", "l1_lb_url": "https://l1-lb-integrationnet.constellationnetwork.io"}
    wallet = DagAccount()
        :return:
        """
        # TODO: Validate and serialize data
        self.network.config(network_info)

        return self

    @property
    def address(self):
        if not self.key_trio or not self.key_trio.get("address"):
            raise ValueError("DagAccount :: Need to login before calling methods on DagAccount.")
        return self.key_trio["address"]

    @property
    def public_key(self):
        return self.key_trio.get("public_key")

    @property
    def private_key(self):
        return self.key_trio.get("private_key")

    def login_with_seed_phrase(self, words: str):
        seed_bytes = Bip39().get_seed_from_mnemonic(words)
        private_key = KeyStore.get_private_key_from_mnemonic(seed_bytes)
        print(words, private_key)
        self.login_with_private_key(private_key)

    def login_with_private_key(self, private_key: str):
        public_key = Bip32.get_public_key_from_private_hex(private_key)
        #public_key = KeyStore.get_public_key_from_private(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        self._set_keys_and_address(private_key, public_key, address)

    def login_with_public_key(self, public_key: str):
        address = KeyStore.get_dag_address_from_public_key(public_key)
        self._set_keys_and_address(None, public_key, address)

    def is_active(self):
        return self.key_trio is not None

    def logout(self):
        self.key_trio = None
        self.emit("session_change", True)

    def observe_session_change(self, listener):
        self.on("session_change", listener)

    def _set_keys_and_address(self, private_key: Optional[str], public_key: str, address: str):
        self.key_trio = {
            "private_key": private_key,
            "public_key": public_key,
            "address": address
        }
        self.emit("session_change", True)

    async def get_balance(self):
        return await self.get_balance_for(self.address)

    async def get_balance_for(self, address: str):
        address_obj = await self.network.get_address_balance(address)
        if address_obj and "balance" in address_obj:
            return Decimal(address_obj["balance"]) * DAG_DECIMALS
        return Decimal(0)

    async def generate_signed_transaction(self, to_address: str, amount: Decimal, fee: Decimal = 0, last_ref=None):
        last_ref = last_ref or await self.network.get_address_last_accepted_transaction_ref(self.address)
        tx, hash_ = KeyStore.prepare_tx(amount, to_address, self.key_trio["address"], last_ref, fee)
        signature = KeyStore.sign(self.key_trio["private_key"], hash_)
        valid = KeyStore.verify(self.public_key, hash_, signature)
        if not valid:
            raise ValueError("Wallet :: Invalid signature.")
        proof = {"id": self.public_key[2:], "signature": signature}
        tx.add_proof(proof=proof)
        return tx.serialize(), hash_


    async def send(self, to_address: str, amount: Decimal, fee: Decimal = 0, auto_estimate_fee=False):
        # TODO: Rate limiting
        normalized_amount = int(amount * DAG_DECIMALS)
        print("Getting last transaction:")
        last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        if fee == Decimal(0) and auto_estimate_fee:
            pending_tx = await self.network.get_pending_transaction(last_ref.get("prev_hash", last_ref.get("hash")))

            if pending_tx:
                balance_obj = await self.network.get_address_balance(self.address)

                if balance_obj and Decimal(balance_obj["balance"]) == normalized_amount:
                    amount -= Decimal(1) / DAG_DECIMALS
                    normalized_amount -= 1

                fee = Decimal(1) / DAG_DECIMALS

        signed_tx, hash_ = await self.generate_signed_transaction(to_address, amount, fee)
        tx_hash = await self.network.post_transaction(signed_tx)

        if tx_hash:
            # TODO: Tax software standards
            return {
                #"timestamp": self.network.get_current_time(),
                "hash": tx_hash,
                "amount": amount,
                "receiver": to_address,
                "fee": fee,
                "sender": self.address,
                "ordinal": last_ref.get("ordinal"),
                "pending": True,
                "status": "POSTED",
            }

    async def wait_for_checkpoint_accepted(self, hash: str):
        txn = None
        try:
            txn = await self.network.get_pending_transaction(hash)
        except Exception:
            pass

        if txn and txn.get("status") == "Waiting":
            return True

        try:
            await self.network.get_transaction(hash)
        except Exception:
            return False

        return True


    async def wait_for_balance_change(self, initial_value: Optional[Decimal] = None):
        if initial_value is None:
            initial_value = await self.get_balance()
            await self.wait(5)

        for _ in range(24):
            result = await self.get_balance()

            if result is not None and result != initial_value:
                return True

            await self.wait(5)

        return False

    async def generate_batch_transactions(self, transfers: List[dict], last_ref: Optional[dict] = None):

        if not last_ref:
            last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        txns = []
        for transfer in transfers:
            transaction, hash_ = await self.generate_signed_transaction(
                transfer["address"],
                transfer["amount"],
                transfer["fee"],
                last_ref
            )

            last_ref = {
                "hash": hash_,
                "ordinal": last_ref["ordinal"] + 1,
            }

            txns.append(transaction)

        return txns

    async def send_batch_transactions(self, transactions: List[dict]):
        if self.network.get_network_version() == "1.0":
            raise Exception("transferDagBatch not available for mainnet 1.0")

        hashes = []
        for txn in transactions:
            hash_ = await self.network.post_transaction(txn)
            hashes.append(hash_)

        return hashes

    async def transfer_dag_batch(self, transfers: List[dict], last_ref: Optional[dict] = None):
        txns = await self.generate_batch_transactions(transfers, last_ref)
        return await self.send_batch_transactions(txns)

    # def create_metagraph_token_client(self, network_info: dict):
    #     return MetagraphTokenClient(self, network_info)

    async def wait(self, time: float = 5.0):
        from asyncio import sleep
        await sleep(time)


class MetagraphTokenClient:
    def __init__(self, account: DagAccount, network_info: Dict[str, Any], token_decimals: int = 8):
        self.account = account
        self.network = MetagraphTokenNetwork(network_info)
        self.token_decimals = token_decimals

    @property
    def network_instance(self):
        return self.network

    @property
    def address(self):
        return self.account.address

    async def get_transactions(self, limit: Optional[int] = None, search_after: Optional[str] = None):
        return await self.network.get_transactions_by_address(self.address, limit, search_after)

    async def get_balance(self):
        return await self.get_balance_for(self.address)

    async def get_balance_for(self, address: str):
        address_obj = await self.network.get_address_balance(address)
        if address_obj and isinstance(address_obj.get("balance"), (int, float)):
            return int(Decimal(address_obj["balance"]) * Decimal(self.token_decimals))
        return 0

    async def get_fee_recommendation(self):
        last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)
        if not last_ref.get("hash"):
            return 0

        last_tx = await self.network.get_pending_transaction(last_ref["hash"])
        if not last_tx:
            return 0

        return 1 / self.token_decimals

    async def transfer(self, to_address: str, amount: int, fee: int = 0, auto_estimate_fee: bool = False):
        normalized_amount = int(Decimal(amount) * Decimal(self.token_decimals))
        last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        if fee == 0 and auto_estimate_fee:
            tx = await self.network.get_pending_transaction(last_ref.get("prevHash") or last_ref.get("hash"))
            if tx:
                address_obj = await self.network.get_address_balance(self.address)
                if address_obj["balance"] == normalized_amount:
                    amount -= self.token_decimals
                    normalized_amount -= 1
                fee = self.token_decimals

        tx = await self.account.generate_signed_transaction(to_address, amount, fee, last_ref)

        if "edge" in tx:
            raise ValueError("Unable to post v1 transaction")

        tx_hash = await self.network.post_transaction(tx)
        if tx_hash:
            return {
                "timestamp": int(time.time() * 1000),
                "hash": tx_hash,
                "amount": amount,
                "receiver": to_address,
                "fee": fee,
                "sender": self.address,
                "ordinal": last_ref["ordinal"],
                "pending": True,
                "status": "POSTED",
            }

    async def wait_for_balance_change(self, initial_value: Optional[int] = None):
        if initial_value is None:
            initial_value = await self.get_balance()
            await self.wait(5)

        for _ in range(24):
            result = await self.get_balance()
            if result is not None and result != initial_value:
                return True
            await self.wait(5)

        return False

    async def generate_batch_transactions(self, transfers: List[Dict[str, Any]], last_ref: Optional[Dict[str, Any]] = None):
        if not last_ref:
            last_ref = await self.network.get_address_last_accepted_transaction_ref(self.address)

        txns = []
        for transfer in transfers:
            transaction, hash_ = await self.account.generate_signed_transaction_with_hash(
                transfer["address"],
                transfer["amount"],
                transfer.get("fee", 0),
                last_ref
            )
            last_ref = {"hash": hash_, "ordinal": last_ref["ordinal"] + 1}
            txns.append(transaction)

        return txns

    async def send_batch_transactions(self, transactions: List[Dict[str, Any]]):
        hashes = []
        for txn in transactions:
            tx_hash = await self.network.post_transaction(txn)
            hashes.append(tx_hash)
        return hashes

    async def transfer_batch(self, transfers: List[Dict[str, Any]], last_ref: Optional[Dict[str, Any]] = None):
        txns = await self.generate_batch_transactions(transfers, last_ref)
        return await self.send_batch_transactions(txns)

    async def wait(self, time_in_seconds: int = 5):
        await asyncio.sleep(time_in_seconds)

