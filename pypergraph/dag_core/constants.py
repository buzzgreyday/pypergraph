from enum import Enum


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

class KeyringNetwork(Enum):
  Constellation = 'Constellation'
  Ethereum = 'Ethereum'

class COIN(Enum):
    DAG = 1137
    ETH = 60

class BIP_44_PATHS(Enum):
    CONSTELLATION_PATH = f"m/44'/{COIN.DAG.value}'/0'/0"
    ETH_WALLET_PATH = f"m/44'/{COIN.ETH.value}'/0'/0"
    ETH_LEDGER_PATH = "m/44'/60'"