from typing import Optional

from pypergraph.core.cross_platform.di.json_storage import JsonStorage


class StateStorageDb:
    def __init__(self, storage_client = None, file_path: Optional[str] = None):
        self.key_prefix = "pypergraph-"
        self.default_storage = JsonStorage(file_path=file_path)  # Fallback storage
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
        await self.storage_client.set_item(full_key, serialized_value)

    async def get(self, key: str = "vault"):
        full_key = self.key_prefix + key
        value = await self.storage_client.get_item(full_key)
        return value if value else None

    async def delete(self, key: str = "vault"):
        full_key = self.key_prefix + key
        await self.storage_client.remove_item(full_key)