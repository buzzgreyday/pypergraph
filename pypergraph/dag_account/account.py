import asyncio
import base58
import hashlib
import time
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any, Dict, List, Optional

from ecdsa import SECP256k1, SigningKey
from eth_keys import keys
from eth_utils import keccak, to_checksum_address, is_checksum_address
from pyee.asyncio import AsyncIOEventEmitter

from pypergraph.dag_core import NetworkId
from pypergraph.dag_core.constants import PKCS_PREFIX, KeyringAssetType
from pypergraph.dag_keystore import KeyStore
from pypergraph.dag_network.network import DagTokenNetwork, MetagraphTokenNetwork


DAG_DECIMALS = Decimal('100000000')  # Assuming DAG uses 8 decimals


class EcdsaAccount(ABC):
    def __init__(self):
        self.tokens: Optional[List[str]] = []
        self.wallet: Optional[SigningKey] = None
        self.assets: Optional[List[Any]] = []
        self.bip44_index: Optional[int] = None
        self.provider = None  # Placeholder for Web3 provider
        self._label: Optional[str] = None

    @property
    @abstractmethod
    def decimals(self) -> int:
        pass

    @property
    @abstractmethod
    def chain_id(self) -> str:
        pass

    @property
    @abstractmethod
    def has_token_support(self) -> bool:
        pass

    @property
    @abstractmethod
    def supported_assets(self) -> List[str]:
        pass

    @abstractmethod
    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        pass

    def get_decimals(self) -> int:
        return self.decimals

    def get_label(self) -> str:
        return self._label

    def create(self, private_key: Optional[str]):
        if private_key:
            self.wallet = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            self.wallet = SigningKey.generate(curve=SECP256k1)
        return self

    def save_token_info(self, address: str):
        pass

    def get_web3_provider(self):
        return self._provider

    def set_web3_provider(self, provider):
        self._provider = provider

    def get_tokens(self) -> Optional[List[str]]:
        return self.tokens.copy() if self.tokens else []

    def set_tokens(self, tokens: List[str]):
        if tokens:
            self.tokens = tokens.copy()

    def get_bip44_index(self) -> Optional[int]:
        return self.bip44_index

    def get_state(self) -> Dict[str, Any]:
        result = {
            "address": self.get_address(),
            "supportedAssets": self.supported_assets,
        }
        if self._label:
            result["label"] = self._label
        if self.tokens:
            result["tokens"] = self.tokens
        return result

    def get_network_id(self):
        return self.chain_id

    def serialize(self, include_private_key: bool = True) -> Dict[str, Any]:
        result = {}
        if include_private_key:
            result["privateKey"] = self.get_private_key()
        if self._label:
            result["label"] = self._label
        if self.tokens:
            result["tokens"] = self.tokens.copy()
        if self.bip44_index is not None:
            result["bip44Index"] = self.bip44_index
        return result

    def deserialize(self, data: Dict[str, Any]):

        private_key = bytes.fromhex(data.get("privateKey"))
        public_key = data.get("publicKey")
        tokens = data.get("tokens")
        bip44_index = data.get("bip44Index")
        label = data.get("label")

        if private_key:
            self.wallet = SigningKey.from_string(private_key, curve=SECP256k1)
        else:
            raise NotImplementedError("EcdsaAccount :: Wallet instance from public key isn't supported.")
            # TODO: This doesn't work since the library doens't seem to have any equivalent
            #self.wallet = Wallet.from_public_key(bytes.fromhex(public_key))

        self._label = label
        self.bip44_index = bip44_index
        self.tokens = tokens or self.tokens
        return self

    # def sign_message(self, msg: str) -> str:
    #     private_key = self.get_private_key_buffer()
    #     msg_hash = eth_util.hash_personal_message(msg.encode())
    #
    #     v, r, s = eth_util.ecsign(msg_hash, private_key)
    #
    #     if not eth_util.is_valid_signature(v, r, s):
    #         raise ValueError("Sign-Verify failed")
    #
    #     return eth_util.strip_hex_prefix(eth_util.to_rpc_sig(v, r, s))

    def recover_signed_msg_public_key(self, msg: str, signature: str) -> str:
        # Compute the hash of the message in Ethereum's personal_sign format
        msg_hash = keccak(text=f"\x19Ethereum Signed Message:\n{len(msg)}{msg}")

        # Decode the signature (remove '0x' prefix if present)
        signature_bytes = bytes.fromhex(signature[2:] if signature.startswith("0x") else signature)
        v, r, s = signature_bytes[-1], signature_bytes[:32], signature_bytes[32:64]

        # Recover the public key
        try:
            public_key = keys.ecdsa_recover(msg_hash,
                                            keys.Signature(vrs=(v, int.from_bytes(r, 'big'), int.from_bytes(s, 'big'))))
        except Exception as e:
            raise ValueError(f"EcdsaAccount :: Failed to recover public key: {e}")

        # Return the public key in hexadecimal format
        return public_key.to_hex()

    def get_address(self) -> str:
        #return self.wallet.get_checksum_address_string()
        vk = self.wallet.get_verifying_key().to_string()

        # Compute the keccak hash of the public key (last 20 bytes is the address)
        public_key = b"\x04" + vk  # Add the uncompressed prefix
        address = keccak(public_key[1:])[-20:]  # Drop the first byte (x-coord prefix)

        return to_checksum_address("0x" + address.hex())

    def get_public_key(self) -> str:
        return self.wallet.get_verifying_key().to_string().hex()

    def get_private_key(self) -> str:
        return self.wallet.to_string().hex()

    def get_private_key_buffer(self):
        return self.wallet.to_string()

class DagAccount(EcdsaAccount):


    network: Optional[DagTokenNetwork] = DagTokenNetwork()
    key_trio: Optional[Dict[str, Optional[str]]] = None
    emitter = AsyncIOEventEmitter()
    decimals = 8
    chain_id = NetworkId.Constellation.value
    has_token_support = False
    supported_assets = ["DAG"]

    def connect(self, network_info: Dict[str, Any]) -> "DagAccount":
        """Configure the network connection."""
        required_keys = {"be_url", "network_id"}
        if not required_keys.issubset(network_info):
            raise ValueError(f"Missing required network keys: {required_keys}")

        self.network = DagTokenNetwork()
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
        private_key = KeyStore.get_private_key_from_mnemonic(words)
        self.login_with_private_key(private_key)

    def login_with_private_key(self, private_key: str):
        public_key = KeyStore.get_public_key_from_private(private_key)
        address = KeyStore.get_dag_address_from_public_key(public_key)
        self._set_keys_and_address(private_key, public_key, address)

    def login_with_public_key(self, public_key: str):
        address = KeyStore.get_dag_address_from_public_key(public_key)
        self._set_keys_and_address(None, public_key, address)

    def is_active(self):
        return self.key_trio is not None

    def logout(self):
        self.key_trio = None
        self.emitter.emit("session_change", True)

    def on_network_change(self):
        pass

    def observe_session_change(self, on_network_change):
        self.emitter.on("session_change", on_network_change)

    def _set_keys_and_address(self, private_key: Optional[str], public_key: str, address: str):
        self.key_trio = {
            "private_key": private_key,
            "public_key": public_key,
            "address": address
        }
        self.emitter.emit("session_change", True)

    async def get_balance(self):
        return await self.get_balance_for(self.address)

    async def get_balance_for(self, address: str):
        address_obj = await self.network.get_address_balance(address)
        if address_obj and "balance" in address_obj:
            return Decimal(address_obj["balance"]) * DAG_DECIMALS
        return 0

    async def generate_signed_transaction(self, to_address: str, amount: int, fee: int = 0, last_ref=None):
        last_ref = last_ref or await self.network.get_address_last_accepted_transaction_ref(self.address)
        tx, hash_ = KeyStore.prepare_tx(amount, to_address, self.key_trio["address"], last_ref, fee)
        signature = KeyStore.sign(self.key_trio["private_key"], hash_)
        valid = KeyStore.verify(self.public_key, hash_, signature)
        if not valid:
            raise ValueError("Wallet :: Invalid signature.")
        proof = {"id": self.public_key[2:], "signature": signature}
        tx.add_proof(proof=proof)
        return tx.serialize(), hash_


    async def send(self, to_address: str, amount: int, fee: int = 0, auto_estimate_fee=False) -> dict:
        """
        Build transaction, sign and send.

        :param to_address: DAG address
        :param amount: Amount with 8 decimals (e.g. 100000000 = 1 DAG)
        :param fee: Fee with 8 deciamls (e.g. 20000 = 0.0002 DAG)
        :param auto_estimate_fee:
        :return:
        """
        # TODO: Rate limiting
        normalized_amount = int(amount * DAG_DECIMALS)
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

        hashes = []
        for txn in transactions:
            hash_ = await self.network.post_transaction(txn)
            hashes.append(hash_)

        return hashes

    async def transfer_dag_batch(self, transfers: List[dict], last_ref: Optional[dict] = None):
        txns = await self.generate_batch_transactions(transfers, last_ref)
        return await self.send_batch_transactions(txns)

    ### --> KEYRING:DAGACCOUNT

    @staticmethod
    def validate_address(address: str) -> bool:
        if not address:
            return False

        valid_len = len(address) == 40
        valid_prefix = address.startswith("DAG")
        valid_parity = address[3].isdigit() and 0 <= int(address[3]) < 10
        base58_part = address[4:]
        valid_base58 = (
            len(base58_part) == 36 and base58_part == base58.b58encode(base58.b58decode(base58_part)).decode()
        )

        return valid_len and valid_prefix and valid_parity and valid_base58

    def get_public_key(self) -> str:
        return self.wallet.get_verifying_key().to_string().hex()

    def get_address(self) -> str:
        return self.get_address_from_public_key(self.get_public_key())

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        public_key = self.recover_signed_msg_public_key(msg, signature)
        actual_address = self.get_address_from_public_key(public_key)
        return says_address == actual_address

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def get_address_from_public_key(self, public_key_hex: str) -> str:
        """
        :param public_key_hex: The private key as a hexadecimal string.
        :return: The DAG address corresponding to the public key (node ID).
        """
        if len(public_key_hex) == 128:
            public_key = PKCS_PREFIX + "04" + public_key_hex
        elif len(public_key_hex) == 130 and public_key_hex[:2] == "04":
            public_key = PKCS_PREFIX + public_key_hex
        else:
            raise ValueError("KeyStore :: Not a valid public key.")

        public_key = hashlib.sha256(bytes.fromhex(public_key)).hexdigest()
        public_key = base58.b58encode(bytes.fromhex(public_key)).decode()
        public_key = public_key[len(public_key) - 36:]

        check_digits = "".join([char for char in public_key if char.isdigit()])
        check_digit = 0
        for n in check_digits:
            check_digit += int(n)
            if check_digit >= 9:
                check_digit = check_digit % 9

        address = f"DAG{check_digit}{public_key}"

        return address

    ### <-- KEYRING:DAGACCOUNT

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


class EthAccount(EcdsaAccount):
    decimals = 18
    chain_id = NetworkId.Ethereum.value
    has_token_support = True
    supported_assets = [KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value]
    tokens = ["0xa393473d64d2F9F026B60b6Df7859A689715d092"]  # LTX

    def save_token_info(self, address: str):
        """Save the token info if not already present in the tokens list."""
        if address not in self.tokens:
            self.tokens.append(address)

    def validate_address(self, address: str) -> bool:
        """Validate an Ethereum address."""
        return is_checksum_address(address)

    def sign_transaction(self, tx):
        """
        Sign an Ethereum transaction with the account's private key.

        tx is an instance of the transaction object from a library like web3.eth.account.
        """
        private_key = self.get_private_key_buffer()
        signed_tx = tx.sign(private_key)
        return signed_tx

    def verify_message(self, msg: str, signature: str, says_address: str) -> bool:
        """Verify if a signed message matches the provided address."""
        public_key = self.recover_signed_msg_public_key(msg, signature)
        actual_address = self.get_address_from_public_key(public_key)
        return to_checksum_address(says_address) == actual_address

    def get_address_from_public_key(self, public_key: str) -> str:
        """Derive the Ethereum address from the public key."""
        address = b"\x04" + hashlib.sha3_256(public_key.encode("utf-8")).digest()
        return to_checksum_address(address)

    def get_encryption_public_key(self) -> str:
        """Get the public key for encryption."""
        # This is a placeholder. Replace it with the appropriate implementation.
        # For example, if using web3py, you can use `eth_account.Account.encrypt()` for encryption keys.
        raise NotImplementedError("Encryption public key generation is not yet implemented.")