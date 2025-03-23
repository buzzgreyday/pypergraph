class NetworkError(Exception):
    """Custom exception for transaction-related errors."""
    def __init__(self, message: str, status: int):
        super().__init__(f"{message} (HTTP {status})")
        self.status = status

