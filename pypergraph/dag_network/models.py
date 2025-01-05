class Balance:

    def __init__(self, data: dict, meta: dict):
        self.ordinal: int = data["ordinal"]
        self.balance: float = data["balance"]
        self.address: str = data["address"]
        self.meta = meta if meta else None

    def __repr__(self):
        return f"Balance(ordinal={self.ordinal}, balance={self.balance}, address='{self.address}', meta='{self.meta}')"

class LastReference:

    def __init__(self, ordinal: int, hash: str):
        self.ordinal = ordinal
        self.hash = hash

    def __repr__(self):
        return f"LastReference(ordinal={self.ordinal}, hash='{self.hash}'"

    def to_dict(self):
        return {'ordinal': self.ordinal, 'hash': f'{self.hash}'}
