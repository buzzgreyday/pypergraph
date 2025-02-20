from enum import Enum
ALIAS_MAX_LEN = 100
BLOCK_MAX_LEN = 100
DAG_MAX = 359230349138528640 * 10 # Ten times the max supply in feb 2025
EPOCH_MAX = 51840000 # 100 years
SNAPSHOT_MAX_KB = 500
STATE_STR_MAX_LEN = 100
SESSION_MIN = 1_000_000_000_000
SESSION_MAX = 9_999_999_999_999 # 13-digit millisecond timestamp
STATE_CHANNEL_SNAPSHOTS_PER_L0_SNAPSHOT = 728 * 100000
PORT_MAX = 65535

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
PKCS_PREFIX = "3056301006072a8648ce3d020106052b8104000a034200"  # Removed last 2 digits. 04 is part of Public Key.

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

class NetworkId(Enum):
  Constellation = 'Constellation'
  Ethereum = 'Ethereum'

class COIN(Enum):
    DAG = 1137
    ETH = 60

# The derivation_path_map together with the seed can be used to derive the extended private key from the public_key
# E.g. "m/44'/{COIN.DAG}'/0'/0" (account 0, index 0); "m/44'/{COIN.DAG}'/0'/1" (account 0, index 1)
class BIP_44_PATHS(Enum):
    CONSTELLATION_PATH = f"m/44'/{COIN.DAG.value}'/0'/0"
    ETH_WALLET_PATH = f"m/44'/{COIN.ETH.value}'/0'/0"
    ETH_LEDGER_PATH = "m/44'/60'"