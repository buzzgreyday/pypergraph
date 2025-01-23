import json
from pathlib import Path

import keyring


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

    async def set(self, key: str | None, value: any):
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