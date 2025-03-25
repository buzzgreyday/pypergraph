import asyncio
import keyring


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