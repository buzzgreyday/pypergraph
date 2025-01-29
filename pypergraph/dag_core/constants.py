from enum import Enum

BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
PKCS_PREFIX = "3056301006072a8648ce3d020106052b8104000a034200"  # Removed last 2 digits. 04 is part of Public Key.

class DERIVATION_PATH(Enum):
    DAG = "DAG"
    ETH = "ETH"
    ETH_LEDGER = "ETH_LEDGER"

class KeyringWalletType(Enum):
  MultiChainWallet = 'MCW'
  CrossChainWallet = 'CCW'
  MultiAccountWallet = 'MAW'  #Single Chain, Multiple seed accounts, MSW
  SingleAccountWallet = 'SAW'  #Single Chain, Single Key account, SKW
  MultiKeyWallet = 'MKW'      #Single Chain, Multiple Key accounts, MKW
  LedgerAccountWallet = "LAW"
  BitfiAccountWallet  = "BAW"

class KeyringAssetType(Enum):
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