from typing import Optional


class LastReference:

    def __init__(self, data: dict):
        self.ordinal: int = data.get("ordinal")
        self.hash: str = data.get("hash")

    def __repr__(self):
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}')"

    def to_dict(self) -> dict:
        """
        Make LastReference object return a dictionary with the last transaction reference associated with the DAG wallet address.

        :return: Dictionary with keys "ordinal" and "hash"
        """
        return {'ordinal': self.ordinal, 'hash': f'{self.hash}'}


class Balance:

    def __init__(self, data: dict, meta: Optional[dict]=None):
        self.ordinal: int = data["ordinal"]
        self.balance: int = data["balance"]
        self.address: str = data["address"]
        self.meta: dict = meta


    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

    # TODO: Make to_dict serialization

