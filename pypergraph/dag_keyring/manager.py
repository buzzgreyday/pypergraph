import asyncio
from pyee.asyncio import AsyncIOEventEmitter

from pypergraph.dag_core import KeyringWalletType
from pypergraph.dag_keyring import SingleAccountWallet, MultiChainWallet, Encryptor

import json
import keyring
from pathlib import Path

class StateStorageDb:
    def __init__(self, storage_client=None):
        self.key_prefix = "pypergraph-"
        self.default_storage = JsonStorage()  # Fallback storage
        self.storage_client = storage_client or self.default_storage

    def set_client(self, client):
        self.storage_client = client or self.default_storage

    def set_prefix(self, prefix: str):
        if not prefix:
            prefix = "pypergraph-"
        elif not prefix.endswith("-"):
            prefix += "-"
        self.key_prefix = prefix

    async def set(self, key: str, value: any):
        full_key = self.key_prefix + key
        serialized_value = value
        self.storage_client.set_item(full_key, serialized_value)

    async def get(self, key: str):
        full_key = self.key_prefix + key
        value = self.storage_client.get_item(full_key)
        if value:
            return value
        return None

    async def delete(self, key: str):
        full_key = self.key_prefix + key
        self.storage_client.remove_item(full_key)


class KeyringStorage:
    """Storage client using the system keyring."""

    @staticmethod
    def get_item(key: str):
        return keyring.get_password("Pypergraph", key)

    @staticmethod
    def set_item(key: str, value: str):
        keyring.set_password("Pypergraph", key, value)

    @staticmethod
    def remove_item(key: str):
        keyring.delete_password("Pypergraph", key)


class JsonStorage:
    """Fallback storage client using a JSON file."""

    def __init__(self, file_path: str = "pypergraph_storage.json"):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps({}))

    def get_item(self, key: str):
        data = self._read_data()
        return data.get(key)

    def set_item(self, key: str, value: str):
        print("Writing:", value)
        data = self._read_data()
        data[key] = value
        self._write_data(data)

    def remove_item(self, key: str):
        data = self._read_data()
        if key in data:
            del data[key]
            self._write_data(data)

    def _read_data(self):
        with self.file_path.open("r") as f:
            return json.load(f)

    def _write_data(self, data):
        with self.file_path.open("w") as f:
            json.dump(data, f, indent=2)

class ObservableStore:
    def __init__(self, initial_state: dict):
        self._state = initial_state
        self._observers = []

    def get_state(self):
        return self._state

    def update_state(self, new_state: dict):
        self._state.update(new_state)
        self.notify_observers()

    def subscribe(self, callback):
        self._observers.append(callback)

    def notify_observers(self):
        for observer in self._observers:
            observer(self._state)

# TODO: EVERYTHING NEEDS A CHECK. Manager has more methods than the ones below. This is only enough to create new wallets. We also need e.g. storage.
class KeyringManager(AsyncIOEventEmitter):

    def __init__(self):
        super().__init__()
        self.encryptor = Encryptor()
        self.storage = StateStorageDb(JsonStorage())
        self.wallets = []
        self.password = ""
        self.mem_store = ObservableStore({"is_unlocked": False, "wallets": []})
        self.on("new_single_account", self.create_single_account_wallet)  # Bind event here

    def is_unlocked(self):
        return bool(self.password)

    async def clear_wallets(self):
        self.wallets = []
        self.mem_store.update_state({ "wallets": [] })

    def new_multi_chain_hd_wallet(self, label: str, seed: str):
        wallet = MultiChainWallet()
        label = label or "Wallet #" + f"{len(self.wallets) + 1}"
        wallet.create(label, seed)
        self.wallets.append(wallet)
        return wallet

    async def create_or_restore_vault(self, label: str, seed: str, password: str):

        if not password:
            raise ValueError("KeyringManager :: A password is required to create or restore a Vault.")
        elif type(password) != str:
            raise ValueError("KeyringManager :: Password has invalid format.")
        else:
            self.password = password

        if not seed:
            raise ValueError("KeyringManager :: A seed is required to create or restore a Vault.")
        # TODO: Validate seed
        # new Error("Seed phrase is invalid.")

        await self.clear_wallets()
        wallet = self.new_multi_chain_hd_wallet(label, seed)
        await self.full_update()

        return wallet

    # creates a single wallet with one chain, creates first account by default, one per chain.
    async def create_single_account_wallet(self, label: str, network, private_key: str):

        wallet = SingleAccountWallet()
        print("Wallet created:", wallet.__dict__)
        label = label or "Wallet #" + f"{len(self.wallets) + 1}"

        wallet.create(network, private_key, label)
        self.wallets.append(wallet)

        self.emit("new_account", wallet.get_accounts()[0]) # :)

        await self.full_update()

        return wallet


    async def full_update(self):

        await self.persist_all_wallets(self.password)
        await self.update_mem_store_wallets()
        self.notify_update()

    async def persist_all_wallets(self, password):
        password = password or self.password
        if type(password) != str:
            raise ValueError("KeyringManager :: Password is not a string")

        self.password = password

        s_wallets = [w.serialize() for w in self.wallets]
        print("Data to be loaded into encryptor:", s_wallets)

        encrypted_string = await self.encryptor.encrypt(self.password, { "wallets": s_wallets })

        # TODO: Add storage
        await self.storage.set("vault", encrypted_string)

    async def update_mem_store_wallets(self):
        wallets = [w.get_state() for w in self.wallets]
        self.mem_store.update_state({"wallets": wallets})
        print("Current Wallet State:", self.mem_store.get_state())

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return bool(self.password == password)

    def notify_update(self):
        self.emit("update", self.mem_store.get_state())

    async def login(self, password: str):
        self.wallets = await self.unlock_wallets(password)
        self.update_unlocked()
        self.notify_update()

    async def unlock_wallets(self, password: str):
        encrypted_vault = await self.storage.get("vault")
        if not encrypted_vault:
            # Support recovering wallets from migration
            self.password = password
            return []

        await self.clear_wallets()
        print("Wallets after clean:", self.mem_store.get_state())
        vault = await self.encryptor.decrypt(password, encrypted_vault) # VaultSerialized
        print()
        print("vault:", vault)
        print()
        self.password = password
        self. wallets = [await self._restore_wallet(w) for w in vault["wallets"]]
        print("Wallets after restore:", self.mem_store.get_state())
        await self.update_mem_store_wallets()
        print("Wallets after memory update", self.mem_store.get_state())
        return self.wallets

    def update_unlocked(self):
        self.mem_store.update_state({"is_unlocked": True})
        self.emit("unlock")

    async def _restore_wallet(self, w_data): # KeyringSerialized
        print()
        print()
        if w_data["type"] == KeyringWalletType.MultiChainWallet.value:
            print("w_data MCW:", w_data)
            wallet = MultiChainWallet()
            wallet.deserialize(w_data)

        elif w_data["type"] == KeyringWalletType.SingleAccountWallet.value:
            wallet = SingleAccountWallet()
            wallet.deserialize(w_data)

        # else if (wData.type === KeyringWalletType.MultiAccountWallet) {
        # wallet = new MultiAccountWallet();
        # wallet.deserialize(wData);
        # }
        # else if (wData.type == = KeyringWalletType.MultiKeyWallet) {
        # wallet = new MultiKeyWallet();
        # wallet.deserialize(wData);
        # }
        else:
            raise ValueError("KeyringManager :: Unknown Wallet type - " + w_data.type + ", support types are [" + KeyringWalletType.MultiChainWallet.value + "," + KeyringWalletType.SingleAccountWallet.value + "]")

        self.wallets.append(wallet)

        return wallet
