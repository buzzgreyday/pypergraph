from typing import Optional, List, Dict, Any, Union

from bip32utils import BIP32Key
from pydantic import BaseModel, Field, model_serializer

from pypergraph.dag_core.constants import NetworkId
from pypergraph.dag_keyring.accounts import EthAccount, DagAccount
from pypergraph.dag_keyring.registry import KeyringRegistry
from pypergraph.dag_keyring.bip import Bip32Helper, Bip39Helper


class HdKeyring(BaseModel):

    accounts: List[Union[DagAccount, EthAccount]] = Field(default_factory=list)
    hd_path: Optional[str] = Field(default=None)
    mnemonic: Optional[str] = Field(default=None)
    extended_key: Optional[str] = Field(default=None)
    root_key: Optional[BIP32Key] = Field(default=None)
    network: Optional[str] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True

    def create(self, mnemonic: str, hd_path: str, network: str, number_of_accounts: int = 1):
        """
        Create a hierarchical deterministic keyring.

        :param mnemonic: Mnemonic phrase.
        :param hd_path: The derivation path for the coin.
        :param network: The network associated with the coin.
        :param number_of_accounts: How many accounts to create.
        :return:
        """
        bip39 = Bip39Helper()
        bip32 = Bip32Helper()
        self.network = network
        inst = HdKeyring()
        inst.mnemonic = mnemonic
        inst.hd_path = hd_path
        # Init from mnemonic
        seed_bytes = bip39.get_seed_bytes_from_mnemonic(mnemonic=inst.mnemonic)
        inst.root_key = bip32.get_hd_root_key_from_seed(seed_bytes=seed_bytes, hd_path=inst.hd_path)
        accounts = inst.create_accounts(number_of_accounts=number_of_accounts)
        inst.deserialize(
            {
                "network": network,
                "accounts": accounts
            }
        )
        return inst

    def create_accounts(self, number_of_accounts: int = 0) -> List[dict]:
        """
        When adding an account (after accounts have been removed), it will add back the ones removed first.

        :param number_of_accounts: The number of accounts to create.

        :returns List[dict]: A list of dictionaries wit bip44 index.
        """
        accounts = []
        for i in range(number_of_accounts):
            accounts.append(
                {
                    "bip44_index": i
                }
            )

        return accounts

    def deserialize(self, data: dict):
        """
        Deserialize then add account (bip44_index) to the keyring being constructed.
        :param data:
        :return:
        """
        if data:
            self.network = data.get("network")
            self.accounts = []
            for d in data.get("accounts"):
                account = self.add_account_at(d.get("bip44_index"))
                # TODO: Add ecdsa account and token support
                account.set_tokens(d.get("tokens"))
                self.accounts.append(account)

    def add_account_at(self, index: int = 0):
        """
        Add account class object with a signing key to the keyring being constructed.

        :param index: Account number (bipIndex).
        :return: EcdsaAccount or DagAccount class object (dag_keyring.accounts) with signing key at self.wallet.
        """
        registry = KeyringRegistry()
        index = index if index >= 0 else len(self.accounts)
        if self.mnemonic:
            private_key = self.root_key.PrivateKey().hex()
            account = registry.create_account(self.network)
            account = account.deserialize(**{ "private_key": private_key, "bip44_index": index })
        else:
            # raise NotImplementedError("HDKeyring :: Wallet from public key isn't supported.")
            public_key = self.root_key.PublicKey()
            account = registry.create_account(self.network)
            account = account.deserialize(**{ "public_key": public_key, "bip44_index": index })

        # self.accounts.append(account)
        return account

    # Read-only wallet
    @staticmethod
    def create_from_extended_key(extended_key: str, network: NetworkId, number_of_accounts: int):
        # TODO: check _init_from...
        inst = HdKeyring()
        inst.extendedKey = extended_key
        inst._init_from_extended_key(extended_key)
        inst.deserialize(
            {
                "network": network,
                "accounts": inst.create_accounts(number_of_accounts)
            }
        )
        return inst

    def get_network(self):
        return self.network

    def get_hd_path(self):
        return self.hd_path

    def get_extended_public_key(self):
        if self.mnemonic:
            return self.root_key.ExtendedKey(private=False)
            # return self.root_key.publicExtendedKey().toString('hex')

        return self.extended_key

    def remove_last_added_account(self):
        self.accounts.pop()

    def export_account (self, account) -> str: # account is IKeyringAccount
        return account.get_private_key()

    def get_accounts(self):
        return self.accounts

    def get_account_by_address(self, address: str): # account is IKeyringAccount
        return next((acc for acc in self.accounts if acc.get_address().lower() == address.lower()), None)

    def remove_account(self, account): # account is IKeyringAccount
        self.accounts = [acc for acc in self.accounts if acc != account] # orig. == account

    def _init_from_extended_key (self, extended_key: str):
        self.root_key = BIP32Key.fromExtendedKey(extended_key)
        # self.root_key = hdkey.fromExtendedKey(extended_key)

    # Serialize all accounts
    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        return {
            "network": self.network,
            "accounts": [acc.serialize(include_private_key=False) for acc in self.accounts]
        } # this.accounts.map(a => a.serialize(false))


# rings.simple_keyring

class SimpleKeyring:

    account = None #IKeyringAccount;
    network: NetworkId.Constellation.value #KeyringNetwork

    def create_for_network(self, network, private_key: str):
        inst = SimpleKeyring()
        inst.network = network
        inst.account = KeyringRegistry().create_account(network).create(private_key)
        return inst


    def get_state(self):
        return {
          "network": self.network,
          "account": self.account.serialize(False)
        }

    def serialize(self):
        return {
          "network": self.network,
          "accounts": [self.account.serialize(True)]
        }

    def deserialize(self, data: dict):
        """
        Deserialize and add an account class object to the keyring being constructed.

        :param data:
        """
        self.network = data.get("network")
        self.account = KeyringRegistry().create_account(data.get("network")).deserialize(data.get("accounts")[0])

    def add_account_at(self, index: int):
        pass
        #throw error

    def get_accounts(self):
        return [self.account]

    def get_account_by_address(self, address: str):
        return self.account if address == self.account.get_address() else None

    def remove_account(self, account):
        pass
     #throw error