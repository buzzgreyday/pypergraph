import json

from pypergraph.dag_core.convert import ddag_to_dag


class LastReference:

    def __init__(self, response: json):
        self.ordinal: int = response.get("ordinal")
        self.hash: str = response.get("hash")

    def __repr__(self):
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}')"

    def to_dict(self) -> dict:
        """
        Make LastReference object return a dictionary with the last transaction reference associated with the DAG wallet address.

        :return: Dictionary with keys "ordinal" and "hash"
        """
        return {'ordinal': self.ordinal, 'hash': f'{self.hash}'}


class Balance:

    def __init__(self, response: json):
        for key in response.keys():
            if key == "data":
                self.ordinal: int = response["data"]["ordinal"]
                self.balance: int = response["data"]["balance"]
                self.address: str = response["data"]["address"]
                self.meta = response["meta"] if "meta" in response else None
            else:
                self.ordinal: int = response["ordinal"]
                self.balance: float = ddag_to_dag(response["balance"])
                self.address = None
                self.meta = response["meta"] if "meta" in response else None

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

    # TODO: Make to_dict serialization

