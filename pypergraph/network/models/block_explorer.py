from datetime import datetime
from typing import Optional, List, Dict

import base58
from pydantic import constr, Field, ConfigDict, BaseModel, field_validator, model_validator

from pypergraph.core.constants import SNAPSHOT_MAX_KB
from pypergraph.network.models.transaction import BaseTransaction, TransactionReference, SignedTransaction, SignatureProof


class Transaction(BaseTransaction):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")
    parent: TransactionReference
    salt: Optional[int] = Field(default=None, ge=0)
    block_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="blockHash")
    snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="snapshotHash")
    snapshot_ordinal: int = Field(alias="snapshotOrdinal", ge=0)
    transaction_original: SignedTransaction = Field(alias="transactionOriginal")
    timestamp: datetime
    proofs: List[SignatureProof] = Field(default_factory=list)
    meta: Optional[Dict] = None

    def __repr__(self):
        return (f"BlockExplorerTransaction(hash={self.hash}, amount={self.amount}, "
                f"source={self.source}, destination={self.destination}, fee={self.fee}, "
                f"parent={self.parent}, salt={self.salt}, block_hash={self.block_hash}, "
                f"snapshot_hash={self.snapshot_hash}, snapshot_ordinal={self.snapshot_ordinal}, "
                f"transaction_original={self.transaction_original}, timestamp={self.timestamp}, "
                f"proofs={self.proofs}, meta={self.meta})")

    @classmethod
    def process_transactions(cls, data: List[dict], meta: Optional[dict] = None) -> List["Transaction"]:
        return [cls.model_validate({**tx, "meta": meta}) for tx in data]

    model_config = ConfigDict(population_by_name=True)

class Snapshot(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")
    ordinal: int = Field(ge=0)
    height: int = Field(ge=0)
    sub_height: int = Field(..., alias="subHeight", ge=0)
    last_snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(..., alias="lastSnapshotHash")
    blocks: List[str]
    timestamp: datetime

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: str) -> datetime:
        # Ensure the timestamp ends with 'Z' (if it's in UTC) and replace it
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")  # Convert to UTC offset format

        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(f"Snapshot :: Invalid timestamp format: {value}")

class CurrencySnapshot(Snapshot):
    fee: int = Field(ge=0)
    owner_address: str = Field(..., alias="ownerAddress") # Validated below
    staking_address: Optional[str] = Field(..., alias="stakingAddress") # Validated below
    size_in_kb: int = Field(..., ge=0, le=SNAPSHOT_MAX_KB, alias="sizeInKB")
    meta: Optional[dict] = None

    @model_validator(mode='before')
    def validate_dag_address(cls, values):
        for address in (values.get('owner_address'), values.get('staking_address')):
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
                    raise ValueError(f"CurrencySnapshot :: Invalid address: {address}")

        return values