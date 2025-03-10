import json
from typing import Optional, List

import keyring

from pathlib import Path

from pydantic import BaseModel, Field

import os

# def get_keystore_path():
#     if os.name == "nt":  # Windows
#         return os.path.join(os.getenv("APPDATA"), "mywallet", "keystore")
#     else:  # Linux/macOS
#         return os.path.expanduser("~/.config/mywallet/keystore")
#
# path = get_keystore_path()
# os.makedirs(path, exist_ok=True)  # Ensure the directory exists
# print(f"Keystore directory: {path}")

class StateStorageDb:
    def __init__(self, storage_client=None):
        """
        Other storage methods can be added to StateStorageDB (e.g. Flask, FastAPI, etc.) by inheriting the class
        in StateStorageDB, e.g. StateStorageDB(PostgreSQLStorage).

        storage = StateStorageDB(PostgreSQLStorage)
        encryptor = Encryptor()
        encrypted_vault = storage.get("vault")
        decrypted_vault = encryptor.decrypt("password", encrypted_vault)
        print(decrypted_vault)

        :param storage_client: Defaults to JsonStorage()
        """
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

    async def set(self, key: Optional[str], value: any):
        key = key or "vault"
        full_key = self.key_prefix + key
        serialized_value = value
        self.storage_client.set_item(full_key, serialized_value)

    async def get(self, key: str = "vault"):
        full_key = self.key_prefix + key
        value = self.storage_client.get_item(full_key)
        if value:
            return value
        return None

    async def delete(self, key: str = "vault"):
        full_key = self.key_prefix + key
        self.storage_client.remove_item(full_key)

"""
The classes below are ready to use for personal wallets. Other storage methods can be added to StateStorageDB 
(e.g. Flask, FastAPI, etc.) by inheriting the class in StateStorageDB, e.g. StateStorageDB(PostgreSQLStorage).

storage = StateStorageDB(PostgreSQLStorage)
encryptor = Encryptor()
encrypted_vault = storage.get("vault")
decrypted_vault = encryptor.decrypt("password", encrypted_vault)
print(decrypted_vault)
"""

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


class ObservableStore(BaseModel):

    is_unlocked: bool = Field(default=False)
    wallets: List[dict] = Field(default_factory=list)
    observers: List = Field(default_factory=list)


    def get_state(self):
        return {"is_unlocked": self.is_unlocked, "wallets": self.wallets}

    def update_state(self, is_unlocked: Optional[bool] = None, wallets: Optional[List[dict]] = None):
        if is_unlocked is not None:
            self.is_unlocked = is_unlocked
        if wallets is not None:
            self.wallets = wallets
        self.notify_observers()

    def subscribe(self, callback):
        self.observers.append(callback)

    def notify_observers(self):
        for observer in self.observers:
            observer(self.get_state())