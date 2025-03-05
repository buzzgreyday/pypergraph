from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Optional

import base58
from pydantic import BaseModel, Field, model_validator, constr, conint, computed_field, ConfigDict

from pypergraph.dag_core.constants import DAG_MAX
from pypergraph.dag_network.models.account import LastReference


class BaseTransaction(BaseModel):
    source: str
    destination: str
    amount: int = Field(ge=0, le=DAG_MAX)
    fee: int = Field(ge=0, lt=DAG_MAX)

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



class PostTransactionResponse(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")

    def __repr__(self) -> str:
        return f"PostTransactionResponse(hash={self.hash!r})"

class PendingTransaction(BaseTransaction):
    parent: LastReference
    salt: int = Field(ge=0)
    transaction_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="hash")
    status: conint(ge=100, le=599)

    @model_validator(mode="before")
    def flatten_data(cls, values: dict) -> dict:
        transaction = values.get("transaction", {})
        parent = values.get("parent", {}),
        return {
            "source": transaction.get("source"),
            "destination": transaction.get("destination"),
            "amount": transaction.get("amount"),
            "fee": transaction.get("fee"),
            "parent": parent,
            "salt": transaction.get("salt"),
            "hash": values.get("hash"),
            "status": values.get("status"),
        }

    def __repr__(self):
        return (f"PendingTransaction(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent_hash={self.parent_hash}, "
                f"parent_ordinal={self.parent_ordinal}, salt={self.salt}, "
                f"transaction_hash={self.transaction_hash}, status={self.status})")


class Transaction(BaseTransaction):
    parent: LastReference
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


class BlockExplorerTransaction(BaseTransaction):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")
    parent: LastReference
    salt: Optional[int] = Field(default=None, ge=0)
    block_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="blockHash")
    snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="snapshotHash")
    snapshot_ordinal: int = Field(alias="snapshotOrdinal", ge=0)
    transaction_original: SignedTransaction = Field(alias="transactionOriginal")
    timestamp: datetime
    proofs: List[SignatureProof] = Field(default_factory=list)
    meta: Optional[Dict] = None # TODO: Validate

    def __repr__(self):
        return (f"BlockExplorerTransaction(hash={self.hash}, amount={self.amount}, "
                f"source={self.source}, destination={self.destination}, fee={self.fee}, "
                f"parent={self.parent}, salt={self.salt}, block_hash={self.block_hash}, "
                f"snapshot_hash={self.snapshot_hash}, snapshot_ordinal={self.snapshot_ordinal}, "
                f"transaction_original={self.transaction_original}, timestamp={self.timestamp}, "
                f"proofs={self.proofs}, meta={self.meta})")

    @classmethod
    def process_transactions(cls, data: List[dict], meta: Optional[dict] = None) -> List["BlockExplorerTransaction"]:
        return [cls.model_validate({**tx, "meta": meta}) for tx in data]


    model_config = ConfigDict(population_by_name=True)