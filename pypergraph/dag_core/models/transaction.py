from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, model_validator


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
    source: str
    destination: str
    amount: int
    fee: int
    parent: Dict[str, Any]
    salt: int

    def __repr__(self):
        return (f"TransactionValue(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent={self.parent}, salt={self.salt})")


class Proof(BaseModel):
    id: str
    signature: str

    @classmethod
    def process_snapshot_proofs(cls, data: list) -> List["Proof"]:
        return [cls(**item) for item in data]

    def __repr__(self):
        return f"Proof(id={self.id}, signature={self.signature})"


class Transaction(BaseModel):
    value: TransactionValue
    proofs: List[Proof] = Field(default_factory=list)

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

    def __repr__(self):
        return (f"Transaction(value={self.value}, proofs={self.proofs})")


class BlockExplorerTransaction(BaseModel):
    hash: str
    amount: int
    source: str
    destination: str
    fee: float
    parent: Dict[str, Any]
    salt: Optional[int] = None
    block_hash: str = Field(alias="blockHash")
    snapshot_hash: str = Field(alias="snapshotHash")
    snapshot_ordinal: int = Field(alias="snapshotOrdinal")
    transaction_original: Transaction = Field(alias="transactionOriginal")
    timestamp: datetime
    proofs: List[Proof] = Field(default_factory=list)
    meta: Optional[Dict] = None

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

    class ConfigDict:
        population_by_name = True