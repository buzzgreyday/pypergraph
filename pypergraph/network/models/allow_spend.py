from typing import List, Optional

from pydantic import BaseModel, Field

from pypergraph.network.models.transaction import SignatureProof


class AllowSpendReference(BaseModel):
    ordinal: int
    hash: str


class AllowSpend(BaseModel):
    source: str
    destination: str
    currency: Optional[str] = Field(default=None, serialization_alias="currencyId")
    amount: int
    fee: int
    parent: AllowSpendReference
    last_valid_epoch_progress: Optional[int] = Field(
        default=None, serialization_alias="lastValidEpochProgress"
    )
    approvers: List[str]
    # ordinal: Optional[int]


class SignedAllowSpend(BaseModel):
    value: AllowSpend
    proofs: List[SignatureProof]


class AllowSpendBlock(BaseModel):
    round_id: str = Field(..., alias="roundId")
    transactions: List[SignedAllowSpend]


class SignedAllowSpendBlock(BaseModel):
    value: AllowSpendBlock
    proofs: List[SignatureProof]


class SpendTransaction(BaseModel):
    allowSpendRef: str
    currency: str
    amount: int
    destination: str


class SpendAction(BaseModel):
    input: SpendTransaction
    output: SpendTransaction
