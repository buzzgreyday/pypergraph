class DERIVATION_PATH:
    DAG = "DAG"
    ETH = "ETH"
    ETH_LEDGER = "ETH_LEDGER"


class COIN:
    DAG = 1137
    ETH = 60

# The derivation_path_map together with the seed can be used to derive the extended private key from the public_key
# E.g. "m/44'/{COIN.DAG}'/0'/0" (account 0, index 0); "m/44'/{COIN.DAG}'/0'/1" (account 0, index 1)
DERIVATION_PATH_MAP = {
    DERIVATION_PATH.DAG: f"m/44'/{COIN.DAG}'/0'/0",
    DERIVATION_PATH.ETH: f"m/44'/{COIN.ETH}'/0'/0",
    DERIVATION_PATH.ETH_LEDGER: "m/44'/60'",
}

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
PKCS_PREFIX = "3056301006072a8648ce3d020106052b8104000a034200"  # Removed last 2 digits. 04 is part of Public Key.
