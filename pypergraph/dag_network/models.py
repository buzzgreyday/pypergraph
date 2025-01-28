from typing import Dict, Any


class Balance:

    def __init__(self, response: dict):
        for key in response.keys():
            if key == "data":
                self.ordinal: int = response["data"]["ordinal"]
                self.balance: float = self.ddag_to_dag(response["data"]["balance"])
                self.address: str = response["data"]["address"]
                self.meta = response["meta"] if "meta" in response else None
            else:
                self.ordinal: int = response["ordinal"]
                self.balance: float = self.ddag_to_dag(response["balance"])
                self.address = None
                self.meta = response["meta"] if "meta" in response else None

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

    @staticmethod
    def get_endpoint(dag_address: str, l0_host: str | None = None, metagraph_id: str | None = None):
        if l0_host and metagraph_id:
            return f"/currency/{dag_address}/balance"
        elif metagraph_id:
            return f"/currency/{metagraph_id}/addresses/{dag_address}/balance"
        elif l0_host and not metagraph_id:
            return f"/dag/{dag_address}/balance"
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

    @staticmethod
    def get_endpoint(address: str):
        """
        :param address: DAG address.
        :return: The endpoint to be added to the host.
        """
        return f"/transactions/last-reference/{address}"

    def to_dict(self) -> dict:
        """
        Make LastReference object return a dictionary with the last transaction reference associated with the DAG wallet address.

        :return: Dictionary with keys "ordinal" and "hash"
        """
        return {'ordinal': self.ordinal, 'hash': f'{self.hash}'}


class PostTransactionResponse:

    def __init__(self, hash: str):
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

    @staticmethod
    def get_endpoint(transaction_hash: str):
        """
        :param transaction_hash:
        :return: The endpoint to ba added to host
        """
        return f"/transactions/{transaction_hash}"
