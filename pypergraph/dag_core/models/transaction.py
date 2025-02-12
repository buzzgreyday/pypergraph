from datetime import datetime
from typing import Type, List, Dict, Optional


class PostTransactionResponse:

    def __init__(self, hash: str):
        self.hash = hash

    def __repr__(self):
        return f"PostTransactionResponse(hash='{self.hash}')"


class PendingTransaction:

    def __init__(self, data: dict):
        transaction = data["transaction"]
        self.source: str = transaction["source"]
        self.destination: str = transaction["destination"]
        self.amount: int = transaction["amount"]
        self.fee: int = transaction["fee"]
        self.parent_hash: str = transaction["parent"]["hash"]
        self.parent_ordinal: int = transaction["parent"]["ordinal"]
        self.salt: str = transaction["salt"]
        self.transaction_hash: str = data["hash"]
        self.status: int = data["status"]

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
    def process_snapshot_proofs(cls, data: list):
        results = []
        for item in data:
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
        cls.proofs = Proof.process_snapshot_proofs(data=data["proofs"]) or []

        return cls

    @classmethod
    def add_value(cls, value: TransactionValue):
        cls.value = value

    @classmethod
    def add_proof(cls, proof: Proof):
        cls.proofs.append(proof)


class BlockExplorerTransaction:
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
        self.proofs: List["Proof"] | List = data["proofs"] if hasattr(data, "proofs") and data["proofs"] else []
        self.meta: Optional[dict] = meta

    @classmethod
    def process_transactions(cls, data: List[dict], meta: Optional[dict] = None) -> List[Type["BlockExplorerTransaction"]]:
        """
        The API returns a json with a 'data' value, sometimes 'meta'. The meta can e.g. point to the next hash.

        :param data: Json 'data' value.
        :param meta: Optional.
        :return:
        """
        transactions = []
        for be_tx in data:
            cls.hash=be_tx["hash"]
            cls.amount=be_tx["amount"]
            cls.source=be_tx["source"]
            cls.destination=be_tx["destination"]
            cls.fee=be_tx["fee"]
            cls.parent=be_tx["parent"]
            cls.salt=be_tx["salt"]
            cls.block_hash=be_tx["blockHash"]
            cls.snapshot_hash=be_tx["snapshotHash"]
            cls.snapshot_ordinal=be_tx["snapshotOrdinal"]
            cls.transaction_original=Transaction.from_dict(be_tx["transactionOriginal"])
            cls.timestamp=datetime.fromisoformat(be_tx["timestamp"])
            cls.proofs=be_tx.get("proofs", [])
            cls.meta=meta

            transactions.append(cls)
        return transactions
