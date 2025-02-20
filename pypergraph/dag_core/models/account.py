from typing import Optional, Dict, Any

import base58
from pydantic import BaseModel, Field, constr, model_validator, field_validator

from pypergraph.dag_core.constants import DAG_MAX


class KeyTrio(BaseModel):

    private_key: Optional[constr(pattern=r"^[a-fA-F0-9]{64}$")] = Field(default=None)
    public_key: constr(pattern=r"^[a-f0-9]{130}$")
    address: str

    @field_validator('address' ,mode='before')
    def validate_dag_address(cls, address):
        if address:
            valid_len = len(address) == 40
            valid_prefix = address.startswith("DAG")
            valid_parity = address[3].isdigit() and 0 <= int(address[3]) < 10
            base58_part = address[4:]
            valid_base58 = (
                len(base58_part) == 36 and base58_part == base58.b58encode(base58.b58decode(base58_part)).decode()
            )

            # If any validation fails, raise an error
            if not (valid_len and valid_prefix and valid_parity and valid_base58):
                raise ValueError(f"Invalid address: {address}")

        return address


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
