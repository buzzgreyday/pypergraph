class Balance:

    def __init__(self, data: dict, meta: dict | None):
        self.ordinal: int = data["ordinal"]
        self.balance: float = self.ddag_to_dag(data["balance"])
        self.address: str = data["address"]
        self.meta = meta if meta is not None else {}

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

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
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}'"

    def to_dict(self) -> dict:
        """
        Make LastReference return a dictionary with DAG address last transaction reference

        :return: Dictionary with keys "ordinal" and "hash"
        """
        return {'ordinal': self.ordinal, 'hash': f'{self.hash}'}
