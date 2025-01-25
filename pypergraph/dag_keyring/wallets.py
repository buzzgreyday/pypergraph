from ecdsa import SigningKey, SECP256k1
from eth_account import Account

from pypergraph.dag_core import BIP_44_PATHS, KeyringAssetType, KeyringWalletType, KeyringNetwork
from .keyrings import HdKeyring, SimpleKeyring
from .bip import Bip39Helper


class MultiAccountWallet:

    SID = 0

    def __init__(self):
        self.type = KeyringWalletType.MultiAccountWallet.value
        self.id = f"{self.type}{self.SID + 1}"
        self.SID += 1
        self.supported_assets = []
        self.label: str = ""
        self.keyring = [] # HdKeyring
        self.mnemonic: str = ""
        self.network: str = "" # KeyringNetwork

    def create(self, network: str, mnemonic: str, label: str, num_of_accounts = 1):
        #if mnemonic:
        #{
        #if (typeof(mnemonic) === 'number')
        #{
        #    mnemonic = Bip39Helper.generateMnemonic(mnemonic);
        #}
        #}
        #else {
        mnemonic = Bip39Helper().generate_mnemonic()
        #}

        self.deserialize({"secret": mnemonic, "type": self.type, "label": label, "network": network, "num_of_accounts": num_of_accounts})

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

    def serialize(self): # Returns KeyringWalletSerialized
        return { "type": self.type, "label": self.label, "network": self.network, "secret": self.export_secret_key(), "rings": [ring.serialize() for ring in self.keyring] }

    def deserialize(self, data: dict):
        self.label = data.get("label")
        self.network = data.get("network")
        self.mnemonic = data.get("secret")

        if self.network == KeyringNetwork.Constellation.value:
            self.supported_assets.append(KeyringAssetType.DAG.value)
            bip44_path = BIP_44_PATHS.CONSTELLATION_PATH
        else:
            self.supported_assets.append(KeyringAssetType.ETH.value)
            self.supported_assets.append(KeyringAssetType.ERC20.value)
            bip44_path = BIP_44_PATHS.ETH_WALLET_PATH.value

        self.keyring = HdKeyring().create(mnemonic=self.mnemonic, hd_path=bip44_path,
                               network=KeyringNetwork.Constellation.value, number_of_accounts=data["num_of_accounts"])

        if data.get("rings"):
            self.keyring.deserialize(data.get("rings")[0])

    def import_account(self, hd_path: str, label: str):
        ValueError("MultiAccountWallet :: Does not support importAccount")
        return None

    def get_accounts(self):
        return self.keyring.get_accounts()

    def get_account_by_address(self, address: str):
        return self.keyring.get_account_by_address(address)

    def add_account(self):
        self.keyring.add_account_at()

    def set_num_of_accounts(self, num: int):
        self.keyring = HdKeyring().create(self.mnemonic, self.keyring.get_hd_path(), self.network, num)

    def remove_account (self, account):
        self.keyring.remove_account(account)

    def export_secret_key(self):
        return self.mnemonic


class MultiKeyWallet:
    # TODO: Check all these
    SID = 0
    def __init__(self):

        self.type = KeyringWalletType.MultiKeyWallet.value
        self.id = f"{self.type}{self.SID + 1}"
        self.SID += 1
        #self.supported_assets =[KeyringAssetType.DAG.value, KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value] Original
        self.supported_assets =[KeyringAssetType.DAG.value, KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value]
        self.label: str = ""
        self.keyrings: [] = []
        self.network = ""

    def create(self, network: str, label: str):
        """
        Create new multi key wallet. These can also be imported.

        :param network: "Constellation" or "Ethereum"
        :param label: Wallet name.
        """

        self.deserialize({ "type": self.type, "lebel": label, "network": network })

    def set_label(self, val: str):
        self.label = val

    def get_label(self) -> str:
        return self.label

    def get_network(self):
        ValueError("MultiChainWallet :: Does not support this method")
        return ""

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
        """
        Deserialize the wallet data into the current instance.

        :param data: A dictionary containing serialized wallet data.
        """
        self.label = data.get("label")
        self.network = data.get("network")
        self.keyrings = []

        if "accounts" in data and len(data["accounts"]) > 0:
            for account in data["accounts"]:
                self.import_account(account.get("privateKey"), account.get("label"))

        if self.network == KeyringNetwork.Ethereum:
            self.supported_assets.extend([KeyringAssetType.ETH, KeyringAssetType.ERC20])
        elif self.network == KeyringNetwork.Constellation:
            self.supported_assets.append(KeyringAssetType.DAG)

    def import_account(self, secret: str, label: str):
        """
        Imports an account using the given secret and label, creates a keyring,
        and adds it to the key_rings list.

        :param secret: The private key of the account to import.
        :param label: A label for the account.
        :return: The first account from the keyring.
        """
        keyring = SimpleKeyring()
        keyring.deserialize({
            "network": self.network,
            "accounts": [{"privateKey": secret, "label": label}]
        })
        self.keyrings.append(keyring)
        return keyring.get_accounts()[0]

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
        ValueError("MultiKeyWallet :: Does not allow removing accounts.")

    def export_secret_key(self):
        ValueError("MultiKeyWallet :: Does not allow exporting secrets.")


class MultiChainWallet:
    SID = 0
    def __init__(self):

        self.type = KeyringWalletType.MultiChainWallet.value
        self.id = f"{self.type}{self.SID + 1}"
        self.SID += 1
        #self.supported_assets =[KeyringAssetType.DAG.value, KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value] Original
        self.supported_assets =[KeyringAssetType.DAG.value, KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value]
        self.label: str = ""
        self.keyrings: [] = []
        self.mnemonic: str = ""

    def create(self, label: str, mnemonic: str = ""):
        """
        If mnemonic is set, restore the wallet. Else, generate mnemonic and create new wallet.

        :param label: Name of the wallet.
        :param mnemonic: Seed phrase.
        """

        self.label = label
        self.mnemonic = mnemonic or Bip39Helper().generate_mnemonic()
        self.deserialize({ "secret": self.mnemonic, "type": self.type, "label": self.label })

    def set_label(self, val: str):
        self.label = val

    def get_label(self) -> str:
        return self.label

    def get_network(self):
        ValueError("MultiChainWallet :: Does not support this method")
        return ""

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
        """
        Main functionality of this MultiChainWallet method is to create hierarchical determinable wallet keyring containing:
        { "network": network, "accounts": [{ "bipIndex44": integer }] }

        :param data: { "label": self.label, "secret": self.mnemonic }
        """
        self.label = data.get("label")
        self.mnemonic = data.get("secret")

        self.keyrings = [
            HdKeyring().create(mnemonic=self.mnemonic, hd_path=BIP_44_PATHS.CONSTELLATION_PATH.value, network=KeyringNetwork.Constellation.value, number_of_accounts=1),
            HdKeyring().create(mnemonic=self.mnemonic, hd_path=BIP_44_PATHS.ETH_WALLET_PATH.value, network=KeyringNetwork.Ethereum.value, number_of_accounts=1)
        ]

        if data.get("rings"):
            for i, r in enumerate(data.get("rings")):
                self.keyrings[i].deserialize(r)

    def import_account(self, hd_path: str, label: str):
        ValueError("MultiChainWallet :: Does not support importAccount")
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
        ValueError("MultiChainWallet :: Does not allow removing accounts.")

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

    def create(self, network: str, private_key: str, label: str):
        """
        Initiates the creation of a new single key wallet.

        :param network:
        :param private_key:
        :param label:
        :return:
        """
        if not private_key:
            private_key = SigningKey.generate(SECP256k1).to_string().hex()

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
        """
        Deserializes the single account data and creates a new simple keyring.

        :param data: { "type": self.type, "label": label, "network": network, "secret": private_key }
        """

        self.label = data.get("label")
        self.network = data.get("network") or KeyringNetwork.Constellation.value
        self.keyring = SimpleKeyring()

        self.keyring.deserialize({"network": self.network, "accounts": [{ "privateKey": data.get("secret") }]})

        if self.network == KeyringNetwork.Ethereum.value:
          self.supported_assets.append(KeyringAssetType.ETH.value)
          self.supported_assets.append(KeyringAssetType.ERC20.value)

        elif self.network == KeyringNetwork.Constellation.value:
          self.supported_assets.append(KeyringAssetType.DAG.value)

    def import_account (self, hdPath: str, label: str):
        ValueError("SingleAccountWallet :: does not support import_account")
        return None

    def get_accounts(self):
        return self.keyring.get_accounts()

    def get_account_by_address(self, address: str):
        return self.keyring.get_account_by_address(address)

    def remove_account(self, account):
        ValueError("SingleChainWallet :: Does not allow removing accounts.")

    def export_secret_key(self) -> str:
        return self.keyring.get_accounts()[0].wallet.to_string().hex()

    def reset_sid(self):
        self.SID = 0