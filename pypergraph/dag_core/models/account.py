from typing import Optional, Dict, Any

from pydantic import BaseModel, Field, constr, model_validator

from pypergraph.dag_core.constants import DAG_MAX


class LastReference(BaseModel):
    ordinal: int = Field(ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

    @model_validator(mode="before")
    def alias_handling(cls, values: dict) -> dict:
        values["hash"] = values.get("parentHash") or values.get("hash")
        values["ordinal"] = values.get("parentOrdinal") or values.get("ordinal")
        return values

    def __repr__(self):
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}')"


class Balance(BaseModel):
    ordinal: int = Field(ge=0)
    balance: int = Field(ge=0, le=DAG_MAX)
    address: Optional[str] = Field(default=None, min_length=40, max_length=128)
    meta: Optional[Dict[str, Any]] = None # TODO: Validate

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

