from typing import Optional, Dict, Any
from pydantic import BaseModel


class LastReference(BaseModel):
    ordinal: int
    hash: str

    def __repr__(self):
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}')"


class Balance(BaseModel):
    ordinal: int
    balance: int
    address: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"
