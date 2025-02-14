from datetime import datetime
from typing import List, Dict, Optional, Any

import base58
from pycparser.c_ast import Default
from pydantic import BaseModel, Field, model_validator, constr, field_validator

from pypergraph.dag_core.constants import DAG_MAX, ORDINAL_MAX


class PostTransactionResponse(BaseModel):
    hash: str

    def __repr__(self) -> str:
        return f"PostTransactionResponse(hash={self.hash!r})"

class PendingTransaction(BaseModel):
    source: str
    destination: str
    amount: int
    fee: int
    parent_hash: str = Field(alias="parentHash")
    parent_ordinal: int = Field(alias="parentOrdinal")
    salt: str
    transaction_hash: str = Field(alias="hash")
    status: int

    @model_validator(mode="before")
    def flatten_data(cls, values: dict) -> dict:
        transaction = values.get("transaction", {})
        parent = transaction.get("parent", {})
        return {
            "source": transaction.get("source"),
            "destination": transaction.get("destination"),
            "amount": transaction.get("amount"),
            "fee": transaction.get("fee"),
            "parent_hash": parent.get("hash"),
            "parent_ordinal": parent.get("ordinal"),
            "salt": transaction.get("salt"),
            "hash": values.get("hash"),
            "status": values.get("status"),
        }

    def __repr__(self):
        return (f"PendingTransaction(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent_hash={self.parent_hash}, "
                f"parent_ordinal={self.parent_ordinal}, salt={self.salt}, "
                f"transaction_hash={self.transaction_hash}, status={self.status})")


class TransactionValue(BaseModel):
    source: str # Validated below
    destination: str # Validated below
    amount: int = Field(ge=0, le=DAG_MAX)
    fee: int = Field(ge=0, le=DAG_MAX)
    parent: Dict[str, Any] # TODO: Validate
    salt: int = Field(default=None, ge=0)

    def __repr__(self):
        return (f"TransactionValue(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent={self.parent}, salt={self.salt})")

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
                    raise ValueError(f"CurrencySnapshot :: Invalid address: {address}")

        return values


class Proof(BaseModel):
    id: constr(pattern=r"^[a-fA-F0-9]{128}$")
    signature: constr(pattern=r"^[a-fA-F0-9]") = Field(min_length=138, max_length=144)

    @classmethod
    def process_snapshot_proofs(cls, data: list) -> List["Proof"]:
        return [cls(**item) for item in data]

    def __repr__(self):
        return f"Proof(id={self.id}, signature={self.signature})"


class Transaction(BaseModel):
    value: TransactionValue
    proofs: List[Proof] = Field(default_factory=list)

    def __repr__(self):
        return f"Transaction(value={self.value}, proofs={self.proofs})"

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(
            value=TransactionValue(**data["value"]),
            proofs=Proof.process_snapshot_proofs(data.get("proofs", []))
        )

    def add_value(self, value: TransactionValue) -> None:
        self.value = value

    def add_proof(self, proof: Proof) -> None:
        self.proofs.append(proof)


class BlockExplorerTransaction(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")
    amount: int = Field(ge=0, le=DAG_MAX)
    source: str # Validated below
    destination: str # Validate below
    fee: int = Field(ge=0, lt=DAG_MAX)
    parent: Dict[str, Any] # TODO: Validate
    salt: Optional[int] = Field(default=None, ge=0)
    block_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="blockHash")
    snapshot_hash: constr(pattern=r"^[a-fA-F0-9]{64}$") = Field(alias="snapshotHash")
    snapshot_ordinal: int = Field(alias="snapshotOrdinal", ge=0, le=ORDINAL_MAX)
    transaction_original: Transaction = Field(alias="transactionOriginal")
    timestamp: datetime
    proofs: List[Proof] = Field(default_factory=list)
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
                    raise ValueError(f"CurrencySnapshot :: Invalid address: {address}")

        return values

    class ConfigDict:
        population_by_name = True