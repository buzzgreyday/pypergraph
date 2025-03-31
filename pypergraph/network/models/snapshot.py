from typing import Optional, List, Dict

from pydantic import BaseModel, Field, constr

from pypergraph.network.models.reward import RewardTransaction
from pypergraph.network.models.transaction import SignatureProof, SignedTransaction


class LastCurrencySnapshotProof(BaseModel):
    leaf_count: int = Field(..., alias="leafCount", ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

class StateChannelSnapshotBinary(BaseModel):
    last_snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="lastSnapshotHash")
    content: List[int]
    fee: int = Field(ge=0)

class SignedStateChannelSnapshotBinary(BaseModel):
    value: StateChannelSnapshotBinary
    proofs: List[SignatureProof]

class StateProof(BaseModel):
    lastStateChannelSnapshotHashesProof: constr(pattern=r"^[a-fA-F0-9]{64}$")
    lastTxRefsProof: constr(pattern=r"^[a-fA-F0-9]{64}$")
    balancesProof: constr(pattern=r"^[a-fA-F0-9]{64}$")
    lastCurrencySnapshotsProof: LastCurrencySnapshotProof

class BlockReference(BaseModel):
    height: int = Field(ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

class Block(BaseModel):
    parent: List[BlockReference]
    transactions: List[Optional[SignedTransaction]]

class SignedBlock(BaseModel):
    # TODO: This is optional?
    value: Optional[Block]
    proofs: Optional[List[SignatureProof]]

class BlockAsActiveTip(BaseModel):
    block: SignedBlock
    usage_count: int = Field(..., alias="usageCount")

class DeprecatedTip(BaseModel):
    block: BlockReference
    deprecated_at: int = Field(alias="deprecatedAt", ge=0)

class SnapshotTips(BaseModel):
    deprecated: List
    remained_active: List = Field(alias="remainedActive")

class GlobalIncrementalSnapshot(BaseModel):
    ordinal: int = Field(ge=0)
    height: int = Field(ge=0)
    sub_height: int = Field(..., alias="subHeight", ge=0)
    last_snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(..., alias="lastSnapshotHash")
    blocks: Optional[List[BlockAsActiveTip]] = None
    state_channel_snapshots: Dict[str, List[SignedStateChannelSnapshotBinary]] = Field(..., alias="stateChannelSnapshots")
    rewards: List[RewardTransaction] # value: RewardTransaction
    epoch_progress: int = Field(..., alias="epochProgress", ge=0)
    next_facilitators: List[constr(pattern=r"^[a-fA-F0-9]{128}$")] = Field(..., alias="nextFacilitators")
    tips: SnapshotTips
    state_proof: StateProof = Field(..., alias="stateProof")
    version: str

class SignedGlobalIncrementalSnapshot(BaseModel):
    value: GlobalIncrementalSnapshot
    proofs: List[SignatureProof]

    @classmethod
    def from_response(cls, response: dict) -> "SignedGlobalIncrementalSnapshot":
        return cls(
            value=GlobalIncrementalSnapshot(**response["value"]),
            proofs=SignatureProof.process_snapshot_proofs(response["proofs"]),
        )

class Ordinal(BaseModel):
    ordinal: int = Field(ge=0, alias="value")

"""BE MODELS: DTO"""
