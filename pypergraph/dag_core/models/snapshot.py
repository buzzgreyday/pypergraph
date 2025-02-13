from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator, Field

from pypergraph.dag_core.models.transaction import Proof


class GlobalSnapshotValue:

    def __init__(self, value: dict):
        self.ordinal: int = value["ordinal"]
        self.height: int = value["height"]
        self.sub_height: int = value["subHeight"]
        self.last_snapshot_hash: str = value["lastSnapshotHash"]
        self.blocks: list = value["blocks"]
        self.state_channel_snapshots: dict = value["stateChannelSnapshot"]
        self.rewards: list = value["rewards"]
        self.epoch_progress: int = value["epochProgress"]
        self.next_facilitators: list = value["nextFacilitators"]
        self.tips: dict = value["tips"]
        self.state_proof: dict = value["stateProof"]
        self.version: str = value["version"]


class GlobalSnapshot:

    def __init__(self, response):
        self.value: GlobalSnapshotValue = GlobalSnapshotValue(response["value"])
        self.proofs: list = Proof.process_snapshot_proofs(response["proofs"])

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
