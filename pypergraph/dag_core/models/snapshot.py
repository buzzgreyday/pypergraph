from datetime import datetime
from typing import Optional, List, Dict

from pydantic import BaseModel, field_validator, Field

from pypergraph.dag_core.models.transaction import Proof


class GlobalSnapshotValue(BaseModel):
    ordinal: int
    height: int
    sub_height: int
    last_snapshot_hash: str = Field(..., alias="lastSnapshotHash")
    blocks: List[str]
    state_channel_snapshots: Dict[str, any] = Field(..., alias="stateChannelSnapshots")
    rewards: List[Dict[str, any]]
    epoch_progress: int
    next_facilitators: List[str] = Field(..., alias="nextFacilitators")
    tips: Dict[str, any]
    state_proof: Dict[str, any] = Field(..., alias="stateProof")
    version: str


class GlobalSnapshot(BaseModel):
    value: GlobalSnapshotValue
    proofs: List[Proof]

    @classmethod
    def from_response(cls, response: dict) -> "GlobalSnapshot":
        return cls(
            value=GlobalSnapshotValue(**response["value"]),
            proofs=Proof.process_snapshot_proofs(response["proofs"]),
        )

"""BE MODELS: DTO"""
class Snapshot(BaseModel):
    hash: str
    ordinal: int
    height: int
    sub_height: int = Field(..., alias="subHeight")
    last_snapshot_hash: str = Field(..., alias="lastSnapshotHash")
    blocks: List[str]
    timestamp: datetime

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: str) -> datetime:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)


class CurrencySnapshot(Snapshot):
    fee: int
    owner_address: str = Field(..., alias="ownerAddress")
    staking_address: Optional[str] = Field(..., alias="stakingAddress")
    size_in_kb: int = Field(..., alias="sizeInKB")
    meta: Optional[dict] = None
