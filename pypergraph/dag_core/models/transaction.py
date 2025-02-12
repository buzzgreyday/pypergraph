import json
from datetime import datetime
from typing import Type, List, Dict, Optional

from pypergraph.dag_core.convert import ddag_to_dag


class PostTransactionResponse:

    def __init__(self, hash: str):
        self.hash = hash

    def __repr__(self):
        return f"PostTransactionResponse(hash='{self.hash}')"


class PendingTransaction:

    def __init__(self, response: json):
        transaction = response["transaction"]
        self.source: str = transaction["source"]
        self.destination: str = transaction["destination"]
        self.amount: int = transaction["amount"]
        self.fee: int = transaction["fee"]
        self.parent_hash: str = transaction["parent"]["hash"]
        self.parent_ordinal: int = transaction["parent"]["ordinal"]
        self.salt: str = transaction["salt"]
        self.transaction_hash: str = response["hash"]
        self.status: int = response["status"]

    def __repr__(self):
        return (f"PendingTransaction(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent_hash={self.parent_hash}, "
                f"parent_ordinal={self.parent_ordinal}, salt={self.salt}, "
                f"transaction_hash={self.transaction_hash}, status={self.status})")


class TransactionValue:
    def __init__(self, source: str, destination: str, amount: int, fee: int, parent: Dict, salt: int):
        self.source: str = source
        self.destination: str = destination
        self.amount: int = amount
        self.fee: int = fee
        self.parent: dict = parent
        self.salt: int = salt

class Proof:
    id: str
    signature: str

    @classmethod
    def process_snapshot_proofs(cls, lst: list):
        results = []
        for item in lst:
            cls.id = item["id"]
            cls.signature = item["signature"]

            results.append(cls)
        return results

class Transaction:
    value: TransactionValue
    proofs: List["Proof"] | list

    @classmethod
    def from_dict(cls, data: dict):
        cls.value = TransactionValue(**data["value"])
        cls.proofs = Proof.process_snapshot_proofs(lst=data["proofs"]) or []

        return cls

    @classmethod
    def add_value(cls, value: TransactionValue):
        cls.value = value

    @classmethod
    def add_proof(cls, proof: Proof):
        cls.proofs.append(proof)


class BETransaction:
    def __init__(
        self,
        data: dict,
        meta: Optional[dict] = None,
    ):
        self.hash: str = data["hash"]
        self.amount: int = data["amount"]
        self.source: str = data["source"]
        self.destination: str = data["destination"]
        self.fee: float = data["fee"]
        self.parent: dict = data["parent"]
        self.salt: Optional[int] = data["salt"] if hasattr(data, "salt") else None
        self.block_hash: str = data["blockHash"]
        self.snapshot_hash: str = data["snapshotHash"]
        self.snapshot_ordinal: int = data["snapshotOrdinal"]
        self.transaction_original: Optional[Transaction | Type["Transaction"]] = data["transactionOriginal"]
        self.timestamp: datetime = datetime.fromisoformat(data["timestamp"])
        self.proofs: List["Proof"] | List = data["proofs"] or []
        self.next: Optional[str] = meta["next"] if hasattr(meta, "next") else None

    @classmethod
    def process_be_transactions(cls, data: List[dict], meta: Optional[dict] = None) -> List["BETransaction"]:
        """
        The API returns a json with a 'data' value, sometimes 'meta'. The meta can e.g. point to the next hash.

        :param data: Json 'data' value.
        :param meta: Optional.
        :return:
        """
        transactions = []
        for be_tx in data:
            transaction = cls(
                hash=be_tx["hash"],
                amount=ddag_to_dag(be_tx["amount"]),
                source=be_tx["source"],
                destination=be_tx["destination"],
                fee=ddag_to_dag(be_tx["fee"]),
                parent=be_tx["parent"],
                salt=be_tx["salt"],
                block_hash=be_tx["blockHash"],
                snapshot_hash=be_tx["snapshotHash"],
                snapshot_ordinal=be_tx["snapshotOrdinal"],
                transaction_original=Transaction.from_dict(be_tx["transactionOriginal"]),
                timestamp=datetime.fromisoformat(be_tx["timestamp"]),
                proofs=be_tx.get("proofs", []),
                next=meta["next"] if hasattr(meta, "next") else None
            )
            transactions.append(transaction)
        return transactions