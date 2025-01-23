from eth_account import Account

from pypergraph.dag_core import BIP_44_PATHS, KeyringAssetType, KeyringWalletType, KeyringNetwork
from .keyrings import HdKeyring, SimpleKeyring


class MultiChainWallet:
    SID = 0
    def __init__(self):

        self.type = KeyringWalletType.MultiChainWallet.value
        self.id = f"{self.type}{self.SID + 1}"
        self.SID += 1
        #self.supported_assets =[KeyringAssetType.DAG.value, KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value] Original
        self.supported_assets =[KeyringAssetType.DAG.value, KeyringAssetType.ETH.value]
        self.label: str = ""
        self.keyrings: [] = [] # Could be many HDKeyrings
        self.mnemonic: str = ""

    # TODO: Add the ability to generate mnemonic
    def create(self, label: str, mnemonic: str):
        self.mnemonic = mnemonic # or  Bip39Helper.generateMnemonic(); Generate mnemonic if None present
        self.deserialize({ "secret":mnemonic, "type": self.type, "label": label })

    def set_label(self, val: str):
        self.label = val

    def get_label(self) -> str:
        return self.label

    def get_network(self):
        ValueError('MultiChainWallet :: Does not support this method')
        return ''

    def get_state(self):
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "supported_assets": self.supported_assets,
            "accounts": [
                {
                    "address": a.get_address(),
                    "network": a.get_network(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    def serialize(self): # Returns KeyringWalletSerialized
        return { "type": self.type, "label": self.label, "secret": self.mnemonic, "rings": [ring.serialize() for ring in self.keyrings] }

    def deserialize(self, data: dict):
        self.label = data.get("label")
        self.mnemonic = data.get("secret")
        self.keyrings = [
            HdKeyring.create(self.mnemonic, BIP_44_PATHS.CONSTELLATION_PATH.value, KeyringNetwork.Constellation.value, 1),
            HdKeyring.create(self.mnemonic, BIP_44_PATHS.ETH_WALLET_PATH.value, KeyringNetwork.Ethereum.value, 1)
        ]
        if data.get("rings"):
            for i, r in enumerate(data.get("rings")):
                self.keyrings[i].deserialize(r)

    def import_account(self, hd_path: str, label: str):
        ValueError('MultiChainWallet :: Does not support importAccount')
        return None


    # getAssets(): string[]
    #{
    # return this.keyrings.reduce < string[] > ((res, w) = > res.concat(w.getAssetList()), []);
    #}
    def get_accounts(self): # IKeyringAccount
        return [account for keyring in self.keyrings for account in keyring.get_accounts()]

    def get_account_by_address(self, address: str): # IKeyringAccount
        account = None
        for keyring in self.keyrings:
            account = keyring.get_account_by_address(address)
            if account:
                break
        return account

    def remove_account(self, account): # IKeyAccount {
        ValueError('MultiChainWallet :: Does not allow removing accounts.')

    def export_secret_key(self):
        return self.mnemonic


    def reset_sid(self):
        self.SID = 0

# accounts.single_account_wallet

# SingleKeyWallet
class SingleAccountWallet:

    SID = 0

    def __init__(self):
        self.type = KeyringWalletType.SingleAccountWallet.value
        self.id = f"{self.type}{self.SID + 1}"
        self.SID += 1
        self.supported_assets = []

        self.keyring = None #SimpleKeyring
        self.network = None #KeyringNetwork;
        self.label: str = ""

    def create(self, network, private_key: str, label: str):
        if not private_key:
            private_key = Account.create().key.hex()

        self.deserialize({ "type": self.type, "label": label, "network": network, "secret": private_key })

    def set_label(self, val: str):
        self.label = val

    def get_label(self) -> str:
        return self.label

    def get_network(self):
        return self.network

    def get_state(self):
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "supported_assets": self.supported_assets,
            "accounts": [
                {
                    "address": a.get_address(),
                    "network": a.get_network(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    def serialize(self):
        return {
          "type": self.type,
          "label": self.label,
          "network": self.network,
          "secret": self.export_secret_key()
        }

    def deserialize(self, data):

        self.label = data.get("label")
        self.network = data.get("network") or KeyringNetwork.Ethereum.value
        self.keyring = SimpleKeyring()

        self.keyring.deserialize({"network": self.network, "accounts": [{ "privateKey": data.get("secret") }]})

        if self.network == KeyringNetwork.Ethereum.value:
          self.supported_assets.append(KeyringAssetType.ETH.value)
          self.supported_assets.append(KeyringAssetType.ERC20.value)

        elif self.network == KeyringNetwork.Constellation.value:
          self.supported_assets.append(KeyringAssetType.DAG)

    def import_account (self, hdPath: str, label: str):
        ValueError('SimpleChainWallet :: does not support importAccount')
        return None

    def get_accounts(self):
        return self.keyring.get_accounts()

    def get_account_by_address(self, address: str):
        return self.keyring.get_account_by_address(address)

    def remove_account(self, account):
        # Does not support removing account
        pass

    def export_secret_key(self) -> str:
        return self.keyring.get_accounts()[0].wallet.to_string().hex()

    def reset_sid(self):
        self.SID = 0