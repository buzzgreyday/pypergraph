import json
import asyncio
import aiofiles
import keyring
from typing import Optional, List
from pathlib import Path

from pydantic import BaseModel, Field


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

    async def set(self, key: Optional[str], value: any):
        key = key or "vault"
        full_key = self.key_prefix + key
        serialized_value = json.dumps(value, separators=(',', ':'))
        await self.storage_client.set_item(full_key, serialized_value)

    async def get(self, key: str = "vault"):
        full_key = self.key_prefix + key
        value = await self.storage_client.get_item(full_key)
        return json.loads(value) if value else None

    async def delete(self, key: str = "vault"):
        full_key = self.key_prefix + key
        await self.storage_client.remove_item(full_key)


class KeyringStorage:
    """Storage client using the system keyring (async via executor)."""

    @staticmethod
    async def get_item(key: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, keyring.get_password, "Pypergraph", key
        )

    @staticmethod
    async def set_item(key: str, value: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, keyring.set_password, "Pypergraph", key, value
        )

    @staticmethod
    async def remove_item(key: str):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, keyring.delete_password, "Pypergraph", key
        )


class JsonStorage:
    """Async JSON file storage using aiofiles."""

    def __init__(self, file_path: str = "pypergraph_storage.json"):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps({}))  # Sync write for initialization

    async def get_item(self, key: str):
        data = await self._read_data()
        return data.get(key) if data else None

    async def set_item(self, key: str, value: str):
        data = await self._read_data()
        data[key] = value
        await self._write_data(data)

    async def remove_item(self, key: str):
        data = await self._read_data()
        if key in data:
            del data[key]
            await self._write_data(data)

    async def _read_data(self):
        async with aiofiles.open(self.file_path, "r") as f:
            contents = await f.read()
            return json.loads(contents) if contents else {}

    async def _write_data(self, data):
        async with aiofiles.open(self.file_path, "w") as f:
            await f.write(json.dumps(data, indent=2))


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