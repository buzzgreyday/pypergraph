from typing import Dict, Any

class Balance:

    def __init__(self, data: dict, meta: dict | None):
        self.ordinal: int = data["ordinal"]
        self.balance: float = self.ddag_to_dag(data["balance"])
        self.address: str = data["address"]
        self.meta = meta if meta is not None else {}

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

    @staticmethod
    def get_endpoint(dag_address: str, metagraph_id: str | None = None):
        if metagraph_id:
            return f"/currency/{metagraph_id}/addresses/{dag_address}/balance"
        else:
            return f"/addresses/{dag_address}/balance"

    @staticmethod
    def ddag_to_dag(balance):
        """Convert dDAG value to DAG value"""
        if balance != 0:
            return float(balance / 100000000)
        elif balance == 0:
            return 0
        else:
            raise ValueError("Balance :: Balance can't be below 0.")

class LastReference:

    def __init__(self, ordinal: int, hash: str):
        self.ordinal = ordinal
        self.hash = hash

    def __repr__(self):
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}')"

    def to_dict(self) -> dict:
        """
        Make LastReference object return a dictionary with the last transaction reference associated with the DAG wallet address.

        :return: Dictionary with keys "ordinal" and "hash"
        """
        return {'ordinal': self.ordinal, 'hash': f'{self.hash}'}


class PostTransactionResponse:

    def __init__(self, hash: str):
        print(hash)
        self.hash = hash

    def __repr__(self):
        return f"PostTransactionResponse(hash='{self.hash}')"


class PendingTransaction:

    def __init__(self, data: Dict[str, Any]):
        transaction = data["transaction"]
        self.source = transaction["source"]
        self.destination = transaction["destination"]
        self.amount = transaction["amount"]
        self.fee = transaction["fee"]
        self.parent_hash = transaction["parent"]["hash"]
        self.parent_ordinal = transaction["parent"]["ordinal"]
        self.salt = transaction["salt"]
        self.transaction_hash = data["hash"]
        self.status = data["status"]

    def __repr__(self):
        return (f"PendingTransaction(source={self.source}, destination={self.destination}, "
                f"amount={self.amount}, fee={self.fee}, parent_hash={self.parent_hash}, "
                f"parent_ordinal={self.parent_ordinal}, salt={self.salt}, "
                f"transaction_hash={self.transaction_hash}, status={self.status})")
