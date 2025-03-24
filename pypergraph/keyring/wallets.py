import re
from typing import Optional, List, Dict, Any, Union

from ecdsa import SigningKey, SECP256k1
from pydantic import Field, BaseModel, model_serializer, model_validator, constr

from pypergraph.core import BIP_44_PATHS, KeyringAssetType, KeyringWalletType, NetworkId

from .accounts.dag_account import DagAccount
from .accounts.eth_account import EthAccount
from .bip import Bip39Helper
from .keyrings import HdKeyring, SimpleKeyring

SID = 0

class MultiAccountWallet(BaseModel):

    type: str = Field(default=KeyringWalletType.MultiAccountWallet.value)
    id: str = Field(default=None)
    supported_assets: List[str] = Field(default=[])
    label: Optional[str] = Field(default=None, max_length=12)
    keyring: HdKeyring = Field(default=None)
    mnemonic: Optional[str] = Field(default=None)
    network: str = Field(default=None)

    @model_validator(mode="after")
    def compute_id(self):
        """Automatically computes the id based on global SID value."""
        global SID
        SID += 1
        self.id = f"{self.type}{SID}"
        return self

    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        """Returns a serialized version of the object."""
        return {
            "type": self.type,
            "label": self.label,
            "secret": self.mnemonic,
            "rings": [ring for ring in self.keyring]
        }

    def create(self, network: str, label: str, num_of_accounts: int = 1, mnemonic: str = None):
        """
        Creates a wallet with a keyring of hierarchical deterministic accounts based on the number BIP44 indexes (num_of_accounts).

        :param network: e.g. "Constellation".
        :param label: "New MAW".
        :param num_of_accounts: Number of BIP44 indexes.
        :param mnemonic: Mnemonic phrase.
        """
        bip39 = Bip39Helper()
        mnemonic = mnemonic or bip39.generate_mnemonic()
        if not bip39.is_valid(mnemonic):
            raise ValueError("MultiAccountWallet :: Not a valid mnemonic phrase.")
        self.deserialize(secret=mnemonic, label=label, network=network, num_of_accounts=num_of_accounts)

    def set_label(self, val: str):
        if not val:
            raise ValueError("MultiAccountWallet :: No label set.")
        self.label = val

    def get_label(self) -> str:
        return self.label

    def get_network(self) -> str:
        return self.network

    def get_state(self) -> Dict[str, Any]:
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

    def deserialize(self, label: str, network: str, secret: str, num_of_accounts: int, rings: Optional[List] = None):
        # Creates keyring

        keyring = HdKeyring()
        self.set_label(label)
        self.network = network
        self.mnemonic = secret

        if self.network == NetworkId.Constellation.value:
            self.supported_assets.append(KeyringAssetType.DAG.value)
            bip44_path = BIP_44_PATHS.CONSTELLATION_PATH
        else:
            self.supported_assets.append(KeyringAssetType.ETH.value)
            self.supported_assets.append(KeyringAssetType.ERC20.value)
            bip44_path = BIP_44_PATHS.ETH_WALLET_PATH.value

        self.keyring = keyring.create(
            mnemonic=self.mnemonic,
            hd_path=bip44_path,
            network=NetworkId.Constellation.value,
            number_of_accounts=num_of_accounts
        )

        if rings:
            self.keyring.deserialize(rings[0])

    @staticmethod
    def import_account():
        """Importing is not supported."""
        raise ValueError("MultiAccountWallet :: Multi account wallets does not support import account.")

    def get_accounts(self) -> List:
        return self.keyring.get_accounts()

    def get_account_by_address(self, address: str):
        return self.keyring.get_account_by_address(address)

    def add_account(self):
        self.keyring.add_account_at()

    def set_num_of_accounts(self, num: int):
        if not num:
            raise ValueError("MultiAccountWallet :: No number of account specified.")
        keyring = HdKeyring()
        self.keyring = keyring.create(
            mnemonic=self.mnemonic, hd_path=self.keyring.get_hd_path(), network=self.network, number_of_accounts=num
        )

    def remove_account (self, account):
        self.keyring.remove_account(account)

    def export_secret_key(self) -> str:
        return self.mnemonic


class MultiKeyWallet(BaseModel):
    # TODO: Check all these

    type: str = Field(default=KeyringWalletType.MultiKeyWallet.value)
    id: str = Field(default=None)
    supported_assets: List[str] = Field(default=[])
    label: Optional[str] = Field(default=None, max_length=12)
    keyrings: List[SimpleKeyring] = Field(default=[])
    private_key: Optional[constr(pattern=r"^[a-fA-F0-9]{64}$")] = Field(default=None)
    network: Optional[str] = Field(default=None)


    @model_validator(mode="after")
    def compute_id(self):
        global SID
        SID += 1
        self.id = f"{self.type}{SID}"
        return self

    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "label": self.label,
            "secret": self.private_key,
            "rings": [ring.model_dump() for ring in self.keyrings]
        }

    def create(self, network: str, label: str):
        """
        Create new multi key wallet. These can also be imported.

        :param network: "Constellation" or "Ethereum"
        :param label: Wallet name.
        """

        self.deserialize(label=label, network=network)

    def set_label(self, val: str):
        if not val:
            raise ValueError("MultiKeyWallet :: No label set.")
        self.label = val

    def get_label(self) -> str:
        return self.label

    @staticmethod
    def get_network():
        raise NotImplementedError("MultiChainWallet :: Multi key wallets does not support this method.")

    def get_state(self) -> Dict[str, Any]:
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


    def deserialize(self, label: str, network: str, accounts: Optional[list] = None):
        """
        Create keyrings.

        :param label:
        :param network:
        :param accounts:
        :return:
        """

        self.set_label(label)
        self.network = network
        self.keyrings = []

        if accounts is not None:
            for account in accounts:
                self.import_account(account.get("private_key"), account.get("label"))

        if self.network == NetworkId.Ethereum:
            self.supported_assets.extend([KeyringAssetType.ETH.value, KeyringAssetType.ERC20.value])
        elif self.network == NetworkId.Constellation:
            self.supported_assets.append(KeyringAssetType.DAG.value)

    def import_account(self, private_key: str, label: str) -> Union[DagAccount, EthAccount]:
        """
        Imports an account using private key and sets a label, creates a keyring and adds it to the keyrings list.

        :param private_key: The private key of the account to import.
        :param label: A label for the account.
        :return: The account from the keyring.
        """
        keyring = SimpleKeyring()
        valid = re.fullmatch(r"^[a-fA-F0-9]{64}$", private_key)
        if not valid:
            ValueError("MultiAccountWallet :: Private key is invalid.")
        keyring.deserialize(network=self.network, accounts=[{"private_key": private_key, "label": label}])
        self.keyrings.append(keyring)
        # Only one account at index 0 present for this wallet type
        return keyring.get_accounts()[0]

    def get_accounts(self) -> List[Union[DagAccount, EthAccount]]: # IKeyringAccount
        return [account for keyring in self.keyrings for account in keyring.get_accounts()]

    def get_account_by_address(self, address: str) -> Union[DagAccount, EthAccount]: # IKeyringAccount
        account = None
        for keyring in self.keyrings:
            account = keyring.get_account_by_address(address)
            if account:
                break
        return account

    @staticmethod
    def remove_account(): # IKeyAccount {
        raise ValueError("MultiKeyWallet :: Does not allow removing accounts.")

    @staticmethod
    def export_secret_key():
        raise ValueError("MultiKeyWallet :: Does not allow exporting secrets.")


class MultiChainWallet(BaseModel):
    type: str = Field(default=KeyringWalletType.MultiChainWallet.value)
    id: str = Field(default=None)
    supported_assets: List[str] = Field(default=[])
    label: Optional[str] = Field(default=None, max_length=12)
    keyrings: List[HdKeyring] = Field(default=[])
    mnemonic: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def compute_id(self):
        global SID
        SID += 1
        self.id = f"{self.type}{SID}"
        return self

    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "label": self.label,
            "secret": self.mnemonic,
            "rings": [ring.model_dump() for ring in self.keyrings]
        }

    def create(self, label: str, mnemonic: Optional[str] = None, rings: Optional[list] = None):
        """
        If mnemonic is set, restore the wallet. Else, generate mnemonic and create new wallet.

        :param label: Name of the wallet.
        :param mnemonic: Seed phrase.
        :param rings: Keyrings.
        """
        bip39 = Bip39Helper()
        self.label = label
        self.mnemonic = mnemonic or bip39.generate_mnemonic()
        if not bip39.is_valid(mnemonic):
            raise ValueError("MultiAccountWallet :: Not a valid mnemonic phrase.")
        self.deserialize(secret=mnemonic, label=label, rings=rings)


    def set_label(self, label: str):
        """
        Set the name of the wallet.

        :param label:
        :return:
        """
        if not label:
            raise ValueError("MultiChainWallet :: No label set.")
        self.label = label

    def get_label(self) -> str:
        """
        Get the name on the wallet.

        :return:
        """
        return self.label

    @staticmethod
    def get_network():
        raise ValueError("MultiChainWallet :: Does not support this method")

    def get_state(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "supported_assets": self.supported_assets,
            "accounts": [
                {
                    "address": a.get_address(),
                    "network": a.get_network_id(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    @staticmethod
    def import_account():
        """Importing account is not supported."""
        raise ValueError("MultiChainWallet :: Multi chain wallet does not support importing account.")

    # TODO
    # getAssets(): string[]
    #{
    # return this.keyrings.reduce < string[] > ((res, w) = > res.concat(w.getAssetList()), []);
    #}

    def get_accounts(self) -> List[Union[DagAccount, EthAccount]]: # IKeyringAccount
        return [account for keyring in self.keyrings for account in keyring.get_accounts()]

    def get_account_by_address(self, address: str) -> Union[DagAccount, EthAccount]: # IKeyringAccount
        account = None
        for keyring in self.keyrings:
            account = keyring.get_account_by_address(address)
            if account:
                break
        return account

    @staticmethod
    def remove_account(): # IKeyAccount {
        raise ValueError("MultiChainWallet :: Does not allow removing accounts.")

    def export_secret_key(self) -> str:
        return self.mnemonic

    def deserialize(self, label: str, secret: str, rings: Optional[list] = None):
        """
        Create keyrings.

        :param label:
        :param secret:
        :param rings:
        :return:
        """

        self.set_label(label)
        self.mnemonic = secret

        self.keyrings = [
            HdKeyring().create(mnemonic=self.mnemonic, hd_path=BIP_44_PATHS.CONSTELLATION_PATH.value, network=NetworkId.Constellation.value, number_of_accounts=1),
            HdKeyring().create(mnemonic=self.mnemonic, hd_path=BIP_44_PATHS.ETH_WALLET_PATH.value, network=NetworkId.Ethereum.value, number_of_accounts=1)
        ]

        if rings:
            for i, r in enumerate(rings):
                self.keyrings[i].deserialize(r)

    @classmethod
    def reset_sid(cls):
        global SID
        SID = 0


class SingleAccountWallet(BaseModel):

    type: str = Field(default=KeyringWalletType.SingleAccountWallet.value)
    id: str = Field(default=None)
    supported_assets: List = Field(default_factory=list)
    label: Optional[str] = Field(default=None, max_length=12)
    keyring: Optional[Any] = Field(default=None)
    network: Optional[str] = Field(default=None)

    @model_validator(mode="after")
    def compute_id(self):
        global SID
        SID += 1
        self.id = f"{self.type}{SID}"
        return self

    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "label": self.label,
            "network": self.network,
            "secret": self.export_secret_key(),
        }

    def create(self, network: str, label: str, private_key: str = None):
        """
        Initiates the creation of a new single key wallet.

        :param network:
        :param private_key:
        :param label:
        :return:
        """
        private_key = private_key or SigningKey.generate(SECP256k1).to_string().hex()
        valid = re.fullmatch(r"^[a-fA-F0-9]{64}$", private_key)
        if not valid:
            ValueError("SingleAccountWallet :: Private key is invalid.")
        self.deserialize(label=label, network=network, secret=private_key)

    def set_label(self, label: str):
        """
        Set the name of the wallet.

        :param label:
        :return:
        """
        if not label:
            raise ValueError("SingleAccountWallet :: No label set.")
        self.label = label

    def get_label(self) -> str:
        return self.label

    def get_network(self) -> str:
        return self.network

    def get_state(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "label": self.label,
            "supported_assets": self.supported_assets,
            "accounts": [
                {
                    "address": a.get_address(),
                    "network": a.get_network_id(),
                    "tokens": a.get_tokens(),
                }
                for a in self.get_accounts()
            ],
        }

    def deserialize(self, network: str, label: str, secret: str):
        """
        Create keyring.

        :param network:
        :param label:
        :param secret:
        :return:
        """
        self.set_label(label)
        self.network = network or NetworkId.Constellation.value
        self.keyring = SimpleKeyring()

        self.keyring.deserialize(network=self.network, accounts=[{ "private_key": secret }])

        if self.network == NetworkId.Ethereum.value:
          self.supported_assets.append(KeyringAssetType.ETH.value)
          self.supported_assets.append(KeyringAssetType.ERC20.value)

        elif self.network == NetworkId.Constellation.value:
          self.supported_assets.append(KeyringAssetType.DAG.value)

    @staticmethod
    def import_account ():
        """Not supported for SingleAccountWallet"""
        raise ValueError("SingleAccountWallet :: does not support importing of account.")

    def get_accounts(self) -> List[Union[DagAccount, EthAccount]]:
        return self.keyring.get_accounts()

    def get_account_by_address(self, address: str) -> Union[DagAccount, EthAccount]:
        return self.keyring.get_account_by_address(address)

    def remove_account(self, account):
        raise ValueError("SingleChainWallet :: Does not allow removing accounts.")

    def export_secret_key(self) -> str:
        return self.keyring.get_accounts()[0].wallet.to_string().hex()

    @classmethod
    def reset_sid(cls):
        global SID
        SID = 0