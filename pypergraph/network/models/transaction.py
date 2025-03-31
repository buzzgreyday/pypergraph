from decimal import Decimal
from enum import Enum
from typing import List, Optional

import base58
from pydantic import BaseModel, Field, model_validator, constr, computed_field, ConfigDict


class Hash(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

class BaseTransaction(BaseModel):
    source: str
    destination: str
    amount: int = Field(ge=0)
    fee: int = Field(ge=0)

    @model_validator(mode='before')
    def validate_dag_address(cls, values):
        for address in (values.get('source'), values.get('destination')):
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

        return values


class TransactionStatus(str, Enum):
    POSTED = "POSTED"
    MEM_POOL = "MEM_POOL"
    DROPPED = "DROPPED"
    CHECKPOINT_ACCEPTED = "CHECKPOINT_ACCEPTED"
    GLOBAL_STATE_PENDING = "GLOBAL_STATE_PENDING"
    CONFIRMED = "CONFIRMED"
    UNKNOWN = "UNKNOWN"


class PendingTransaction(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")
    sender: Optional[str] = None
    receiver: Optional[str] = None
    amount: Optional[int] = None
    ordinal: Optional[int] = None
    status: Optional[TransactionStatus] = None
    pending: Optional[bool] = None
    pending_msg: Optional[str] = None
    timestamp: int
    fee: Optional[int] = None

    model_config = ConfigDict(
        use_enum_values=True
    )

class TransactionReference(BaseModel):
    ordinal: int = Field(ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

    @model_validator(mode="before")
    def alias_handling(cls, values: dict) -> dict:
        values["hash"] = values.get("parentHash") or values.get("hash")
        values["ordinal"] = values.get("parentOrdinal") or values.get("ordinal")
        return values

class Transaction(BaseTransaction):
    parent: TransactionReference
    salt: int = Field(default=None, ge=0)

    def __repr__(self):
        return (f"TransactionValue(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent={self.parent}, salt={self.salt})")


    @computed_field
    @property
    def encoded(self) -> str:
        """Automatically generates the encoded signing string"""
        components = [
            ("2", False),  # Parent count (fixed)
            (self.source, True),
            (self.destination, True),
            (format(self.amount, "x"), True),  # Hex amount
            (self.parent.hash, True),
            (str(self.parent.ordinal), True),
            (str(self.fee), True),
            (self.to_hex_string(self.salt), True)
        ]

        return "".join(
            f"{len(str(value))}{value}" if include_length else str(value)
            for value, include_length in components
        )

    @staticmethod
    def to_hex_string(val):
        val = Decimal(val)
        if val < 0:
            b_int = (1 << 64) + int(val)
        else:
            b_int = int(val)
        return format(b_int, "x")



class SignatureProof(BaseModel):
    id: constr(pattern=r"^[a-fA-F0-9]{128}$")
    signature: constr(pattern=r"^[a-fA-F0-9]") = Field(min_length=138, max_length=144)

    @classmethod
    def process_snapshot_proofs(cls, data: list) -> List["SignatureProof"]:
        return [cls(**item) for item in data]

    def __repr__(self):
        return f"Proof(id={self.id}, signature={self.signature})"


class SignedTransaction(BaseModel):
    value: Transaction
    proofs: List[SignatureProof] = Field(default_factory=list)

    def __repr__(self):
        return f"Transaction(value={self.value}, proofs={self.proofs})"

    def add_value(self, value: Transaction) -> None:
        self.value = value

    def add_proof(self, proof: SignatureProof) -> None:
        self.proofs.append(proof)


class SignedData(BaseModel):
    value: dict
    proofs: List[SignatureProof] = Field(default_factory=list)

    def __repr__(self):
        return f"Transaction(value={self.value}, proofs={self.proofs})"

    def add_value(self, value: dict) -> None:
        self.value = value

    def add_proof(self, proof: SignatureProof) -> None:
        self.proofs.append(proof)

class DelegatedStakeReference(BaseModel):
    ordinal: int = Field(ge=0)
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

class CreateDelegatedStake(BaseModel):
    source: str
    node_id: constr(pattern=r"^[a-fA-F0-9]{128}$") = Field(alias="nodeId")
    amount: int = Field(ge=0)
    fee: int = Field(ge=0)
    token_lock_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="tokenLockRef")
    parent: DelegatedStakeReference

class SignedCreateDelegatedStake(BaseModel):
    value: CreateDelegatedStake
    proofs: List[SignatureProof]

class WithdrawDelegatedStake(BaseModel):
    source: str = Field()
    stake_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="stakeRef")

class SignedWithdrawDelegatedStake(BaseModel):
    value: WithdrawDelegatedStake
    proofs: List[SignatureProof]

class DelegatedStakeInfo(BaseModel):
    node_id: constr(pattern=r"^[a-fA-F0-9]{128}$") = Field(alias="nodeId")
    accepted_ordinal: int = Field(alias="acceptedOrdinal", ge=0)
    token_lock_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="tokenLockRef")
    amount: int = Field(ge=0)
    fee: int = Field(ge=0)
    withdrawal_start_epoch: int = Field(alias="withdrawalStartEpoch", ge=0)
    withdrawal_end_epoch: int = Field(alias="withdrawalEndEpoch", ge=0)

class DelegatedStakesInfo(BaseModel):
    address: str
    active_delegated_stakes: List[DelegatedStakeInfo]
    pending_withdrawals: List[DelegatedStakeInfo]

class CreateNodeCollateral(BaseModel):
    source: str
    node_id: constr(pattern=r"^[a-fA-F0-9]{128}$") = Field(alias="nodeId")
    amount: int = Field(ge=0)
    fee: int = Field(ge=0)
    token_lock_ref: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="tokenLockRef")
    parent: TransactionReference

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

# TODO: Node_params, see cluster_info