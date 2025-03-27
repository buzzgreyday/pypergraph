import json
import aiofiles
from pathlib import Path


class JsonStorage:
    """Async JSON file storage using aiofiles."""

    def __init__(self, file_path: str = None):
        if not file_path:
            raise ValueError("JsonStorage :: Please provide a file path.")
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            self.file_path.write_text(json.dumps({}))  # Sync write for initialization

    async def get_item(self, key: str):
        data = await self._read_data()
        return data.get(key)

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
            return json.loads(contents) if contents else None

    async def _write_data(self, data):
        async with aiofiles.open(self.file_path, "w") as f:
            await f.write(json.dumps(data, indent=2))