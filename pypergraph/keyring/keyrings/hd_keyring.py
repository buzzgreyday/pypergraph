from typing import Optional, List, Dict, Any, Union

from bip32utils import BIP32Key
from pydantic import BaseModel, Field, model_serializer, ConfigDict
from typing_extensions import Self

from pypergraph.core.constants import NetworkId
from pypergraph.keyring.keyrings.registry import KeyringRegistry
from ..accounts.eth_account import EthAccount
from ..accounts.dag_account import DagAccount
from ..bip_helpers.bip32_helper import Bip32Helper
from ..bip_helpers.bip39_helper import Bip39Helper


class HdKeyring(BaseModel):
    """
    Hierarchical Deterministic Keyring: BIP32

    """


    accounts: List[Union[DagAccount, EthAccount]] = Field(default_factory=list)
    hd_path: Optional[str] = Field(default=None)
    mnemonic: Optional[str] = Field(default=None)
    extended_key: Optional[str] = Field(default=None)
    root_key: Optional[BIP32Key] = Field(default=None)
    network: Optional[str] = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Serialize all accounts
    @model_serializer
    def model_serialize(self) -> Dict[str, Any]:
        return {
            "network": self.network,
            "accounts": [acc.serialize(include_private_key=False) for acc in self.accounts]
        }

    def create(self, mnemonic: str, hd_path: str, network: str, number_of_accounts: int = 1) -> Self:
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

    def create_accounts(self, number_of_accounts: int = 0) -> List[Dict]:
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

    def add_account_at(self, index: int = 0) -> Union[DagAccount, EthAccount]:
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
            account = account.deserialize(private_key=private_key, bip44_index=index)
        else:
            # raise NotImplementedError("HDKeyring :: Wallet from public key isn't supported.")
            public_key = self.root_key.PublicKey()
            account = registry.create_account(self.network)
            account = account.deserialize(public_key=public_key, bip44_index=index)

        # self.accounts.append(account)
        return account

    # Read-only wallet
    def create_from_extended_key(self, extended_key: str, network: NetworkId, number_of_accounts: int) -> Self:
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

    def get_network(self) -> str:
        return self.network

    def get_hd_path(self) -> str:
        return self.hd_path

    def get_extended_public_key(self) -> str:
        if self.mnemonic:
            return self.root_key.ExtendedKey(private=False).hex()

        return self.extended_key

    def remove_last_added_account(self):
        self.accounts.pop()

    def export_account (self, account) -> str: # account is IKeyringAccount
        return account.get_private_key()

    def get_accounts(self) -> List:
        return self.accounts

    def get_account_by_address(self, address: str) -> Union[DagAccount, EthAccount]: # account is IKeyringAccount
        return next((acc for acc in self.accounts if acc.get_address().lower() == address.lower()), None)

    def remove_account(self, account): # account is IKeyringAccount
        self.accounts = [acc for acc in self.accounts if acc != account] # orig. == account

    def _init_from_extended_key (self, extended_key: str):
        self.root_key = BIP32Key.fromExtendedKey(extended_key)