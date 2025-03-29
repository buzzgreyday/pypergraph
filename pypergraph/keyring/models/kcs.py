from dataclasses import dataclass
from typing import Optional


@dataclass
class KeyringAssetInfo:
    id: str
    label: str
    symbol: str
    decimals: int
    native: Optional[bool] = None
    network: Optional[str] = None
    address: Optional[str] = None
