from enum import Enum
ALIAS_MAX_LEN = 100
SNAPSHOT_MAX_KB = 500
STATE_STR_MAX_LEN = 100
STATE_CHANNEL_SNAPSHOTS_PER_L0_SNAPSHOT = 728 * 100000
PORT_MAX = 65535

# SECP256k1 curve order (for canonical signature adjustment) from https://asecuritysite.com/secp256k1/
SECP256K1_ORDER = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
PKCS_PREFIX = "3056301006072a8648ce3d020106052b8104000a034200"  # Removed last 2 digits. 04 is part of Public Key.

POST_TRANSACTION_ERRORS = (
        "TransactionLimited", "ParentOrdinalLowerThenLastTxOrdinal", "HasNoMatchingParent", "InsufficientBalance",
        "AddressLocked", "Conflict", "SameSourceAndDestinationAddress", "NotSignedBySourceAddressOwner"
)

#            $DAG transaction has been rejected. Returned one of rejection reasons:
#               - TransactionLimited - the limit for fee-less transactions per address depends on the address balance and time passed since last accepted transaction.
#               - ParentOrdinalLowerThenLastTxOrdinal - The transaction's ordinal number must be +1 relative to the last accepted transaction.
#               - HasNoMatchingParent - the parent's hash of the transaction must point to the existing accepted transaction.
#               - InsufficientBalance - the amount value of the transaction is higher than the balance of the source address.
#               - AddressLocked - the address is locked by the network, and transactions can't be made.
#               - Conflict - such transaction has been already accepted by the network.
#               - SameSourceAndDestinationAddress - the source and destination addresses should be different.
#               - NotSignedBySourceAddressOwner - the transaction should be signed exclusively by the key of the source address.

class DERIVATION_PATH(str, Enum):
    DAG = "DAG"
    ETH = "ETH"
    ETH_LEDGER = "ETH_LEDGER"

class KeyringWalletType(str, Enum):
  MultiChainWallet = 'MCW'
  CrossChainWallet = 'CCW'
  MultiAccountWallet = 'MAW'  #Single Chain, Multiple seed accounts, MSW
  SingleAccountWallet = 'SAW'  #Single Chain, Single Key account, SKW
  MultiKeyWallet = 'MKW'      #Single Chain, Multiple Key accounts, MKW
  LedgerAccountWallet = "LAW"
  BitfiAccountWallet  = "BAW"

class KeyringAssetType(str, Enum):
  DAG = 'DAG'
  ETH = 'ETH'
  ERC20 = 'ERC20'

class NetworkId(str, Enum):
  Constellation = 'Constellation'
  Ethereum = 'Ethereum'

class COIN(Enum):
    DAG = 1137
    ETH = 60

class BIP_44_PATHS(str, Enum):
    CONSTELLATION_PATH = f"m/44'/{COIN.DAG.value}'/0'/0" # Index is added here + '/0'
    ETH_WALLET_PATH = f"m/44'/{COIN.ETH.value}'/0'/0" # Index is added here + '/0'
    ETH_LEDGER_PATH = "m/44'/60'"
