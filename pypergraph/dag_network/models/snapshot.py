from datetime import datetime
from typing import Optional, List, Dict, Any

import base58
from pydantic import BaseModel, field_validator, Field, model_validator, constr

from pypergraph.dag_core.constants import DAG_MAX, SNAPSHOT_MAX_KB, BLOCK_MAX_LEN,EPOCH_MAX
from pypergraph.dag_network.models.transaction import SignatureProof

class LastCurrencySnapshotProof(BaseModel):
    leaf_count: int = Field(..., alias="leafCount", ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

class StateProof(BaseModel):
    lastStateChannelSnapshotHashesProof: constr(pattern=r"^[a-fA-F0-9]{64}$")
    lastTxRefsProof: constr(pattern=r"^[a-fA-F0-9]{64}$")
    balancesProof: constr(pattern=r"^[a-fA-F0-9]{64}$")
    lastCurrencySnapshotsProof: LastCurrencySnapshotProof

class GlobalSnapshotValue(BaseModel):
    ordinal: int = Field(ge=0)
    height: int = Field(ge=0)
    sub_height: int = Field(..., alias="subHeight", ge=0)
    last_snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(..., alias="lastSnapshotHash")
    blocks: List[str] = Field(max_length=BLOCK_MAX_LEN)
    state_channel_snapshots: Dict[str, List[Dict]] = Field(..., alias="stateChannelSnapshots") # TODO: Validate
    rewards: List[Dict[str, Any]] # TODO: Validate
    epoch_progress: int = Field(..., alias="epochProgress", ge=0, le=EPOCH_MAX)
    next_facilitators: List[constr(pattern=r"^[a-fA-F0-9]{128}$")] = Field(..., alias="nextFacilitators")
    tips: Dict[str, Any] # TODO: Validate
    state_proof: StateProof = Field(..., alias="stateProof")
    version: str


class GlobalSnapshot(BaseModel):
    value: GlobalSnapshotValue
    proofs: List[SignatureProof]

    @classmethod
    def from_response(cls, response: dict) -> "GlobalSnapshot":
        return cls(
            value=GlobalSnapshotValue(**response["value"]),
            proofs=SignatureProof.process_snapshot_proofs(response["proofs"]),
        )

"""BE MODELS: DTO"""
class Snapshot(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")
    ordinal: int = Field(ge=0)
    height: int = Field(ge=0)
    sub_height: int = Field(..., alias="subHeight", ge=0)
    last_snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(..., alias="lastSnapshotHash")
    blocks: List[str] = Field(max_length=BLOCK_MAX_LEN)
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
    fee: int = Field(ge=0, lt=DAG_MAX)
    owner_address: str = Field(..., alias="ownerAddress") # Validated below
    staking_address: Optional[str] = Field(..., alias="stakingAddress") # Validated below
    size_in_kb: int = Field(..., ge=0, le=SNAPSHOT_MAX_KB, alias="sizeInKB")
    meta: Optional[dict] = None # TODO: Validate

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