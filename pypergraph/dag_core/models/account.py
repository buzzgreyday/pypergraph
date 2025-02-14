from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, constr

from pypergraph.dag_core.constants import ORDINAL_MAX, DAG_MAX


class LastReference(BaseModel):
    ordinal: int = Field(ge=0, le=ORDINAL_MAX)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

    def __repr__(self):
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}')"


class Balance(BaseModel):
    ordinal: int = Field(ge=0, le=ORDINAL_MAX)
    balance: int = Field(ge=0, le=DAG_MAX)
    address: Optional[str] = Field(default=None, min_length=40, max_length=128)
    meta: Optional[Dict[str, Any]] = None # TODO: Validate

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

