from typing import List, Optional

from pydantic import BaseModel, Field, constr

from pypergraph.network.models.transaction import SignatureProof

"""
Methods
-------

    POST /token-locks
    GET /token-locks/{hash}
    GET /token-locks/last-reference/{address}
    
"""

class TokenLockReference(BaseModel):
    """
    GET /token-locks/last-reference/{address}
    """
    ordinal: int = Field(description="The ordinal number of the token lock transaction", ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

class TokenLock(BaseModel):
    """
    Token lock transactions are used to create delegated stakes, etc.
    POST /token-locks
    """
    source: str
    amount: int
    fee: int
    parent: TokenLockReference
    currency_id: Optional[str] = Field(
        description="Optional currency identifier for the token lock. NULL for DAG.",
        default=None,
        alias="currencyId"
    )
    unlock_epoch: Optional[int] = Field(
        description="Optional epoch progress value when the tokens will be unlocked. NULL for indefinite lock.",
        default=None,
        ge=0,
        alias="unlockEpoch"
    )

class SignedTokenLock(BaseModel):
    value: TokenLock
    proofs: List[SignatureProof]


