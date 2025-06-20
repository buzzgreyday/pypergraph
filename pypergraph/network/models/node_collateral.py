from typing import List

from pydantic import constr, BaseModel, Field

from pypergraph.network.models.transaction import SignatureProof


class NodeCollateralReference(BaseModel):
    ordinal: int = Field(ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")


class CreateNodeCollateral(BaseModel):
    source: str
    node_id: constr(pattern=r"^[a-fA-F0-9]{128}$") = Field(alias="nodeId")
    amount: int = Field(ge=0)
    fee: int = Field(ge=0)
    token_lock_ref_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(
        alias="tokenLockRefHash"
    )
    parent: NodeCollateralReference


class SignedCreateNodeCollateral(BaseModel):
    value: CreateNodeCollateral
    proofs: List[SignatureProof]


class WithdrawNodeCollateral(BaseModel):
    source: str
    collateral_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="collateralRef")


class SignedWithdrawNodeCollateral(BaseModel):
    value: WithdrawNodeCollateral
    proofs: List[SignatureProof]


class NodeCollateralInfo(BaseModel):
    node_id: constr(pattern=r"^[a-fA-F0-9]{128}$") = Field(alias="nodeId")
    accepted_ordinal: int = Field(alias="acceptedOrdinal", ge=0)
    token_lock_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="tokenLockRef")
    amount: int = Field(ge=0)
    fee: int = Field(ge=0)
    withdrawal_start_epoch: int = Field(alias="withdrawalStartEpoch", ge=0)
    withdrawal_end_epoch: int = Field(alias="withdrawalEndEpoch", ge=0)


class NodeCollateralsInfo(BaseModel):
    address: str
    active_node_collaterals: List[NodeCollateralInfo]
    pending_withdrawals: List[NodeCollateralInfo]
