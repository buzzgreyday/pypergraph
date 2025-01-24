from mnemonic import Mnemonic

from pypergraph.dag_core.constants import KeyringNetwork
from pypergraph.dag_keyring.accounts import EcdsaAccount, DagAccount
from pypergraph.dag_keyring.registry import KeyringRegistry
from pypergraph.dag_keyring.bip import Bip32Helper, Bip39Helper


class HdKeyring:

    accounts: [] = []
    hd_path: str = ""
    mnemonic: str = ""
    extended_key: str = ""
    root_key = None
    network: str = ""

    # Read-only wallet
    @staticmethod
    def create_from_extended_key(extended_key: str, network: KeyringNetwork, number_of_accounts: int):
        # TODO: check _init_from...
        inst = HdKeyring()
        inst.extendedKey = extended_key
        inst._init_from_extended_key(extended_key)
        inst.deserialize( { "network": network, "accounts": inst.create_accounts(number_of_accounts) })
        return inst

    def create(self, mnemonic: str, hd_path: str, network, number_of_accounts: int = 1):
        """
        Create a hierarchical deterministic keyring.

        :param mnemonic: Mnemonic phrase.
        :param hd_path: The derivation path for the coin.
        :param network: The network associated with the coin.
        :param number_of_accounts: How many accounts to create.
        :return:
        """

        self.network = network
        inst = HdKeyring()
        inst.mnemonic = mnemonic
        inst.hd_path = hd_path
        seed_bytes = Bip39Helper().get_seed_bytes_from_mnemonic(mnemonic=inst.mnemonic)
        inst.root_key = Bip32Helper().get_hd_root_key_from_seed(seed_bytes=seed_bytes, hd_path=inst.hd_path)
        inst.deserialize( { "network": network, "accounts": inst.create_accounts(number_of_accounts) })
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

    # Serialize all accounts
    def serialize(self):
        return { "network": self.network, "accounts": [acc.serialize(False) for acc in self.accounts] } # this.accounts.map(a => a.serialize(false))


    def deserialize(self, data: dict):
        """
        Deserialize then add account (bip44Index) to the keyring being constructed.
        :param data:
        :return:
        """
        if data:
            self.network = data.get("network")
            self.accounts = []
            for d in data.get("accounts"):
                account = self.add_account_at(d.get("bip44Index"))
                # TODO: Add ecdsa account and token support
                account.set_tokens(d.get("tokens"))
                #self.accounts.append(account)


    def create_accounts(self, number_of_accounts=0):
        """
        When adding an account (after accounts have been removed), it will add back the ones removed first.

        Args:
            number_of_accounts (int): The number of accounts to create.

        Returns:
            list[dict]: A list of dictionaries representing the accounts.
        """
        accounts = []
        for i in range(number_of_accounts):
            accounts.append({"bip44Index": i})

        return accounts

    def remove_last_added_account(self):
        self.accounts.pop()

    def add_account_at(self, index: int):
        """
        Add account class object with a signing key to the keyring being constructed.

        :param index: Account number (bipIndex).
        :return: EcdsaAccount or DagAccount class object (dag_keyring.accounts) with signing key at self.wallet.
        """
        index = index if index >= 0 else len(self.accounts)
        if self.mnemonic:
            private_key = self.root_key.PrivateKey().hex()
            account = KeyringRegistry().create_account(self.network).deserialize({ "privateKey": private_key, "bip44Index": index })
        else:
            # raise NotImplementedError("HDKeyring :: Wallet from public key isn't supported.")
            public_key = self.root_key.PublicKey()
            account = KeyringRegistry().create_account(self.network).deserialize({ "publicKey": public_key, "bip44Index": index })

        self.accounts.append(account)

        return account

    def get_accounts(self):
        return self.accounts

    """ PRIVATE METHODS """

    # TODO: Library
    def _init_from_mnemonic(self, mnemonic):
        pass


    def _init_from_extended_key (self, extended_key: str):
        # TODO:
        self.extended_key = extended_key
        # self.root_key = hdkey.fromExtendedKey(extended_key)

    def export_account (self, account) -> str: # account is IKeyringAccount
        return account.get_private_key()

    def get_account_by_address(self, address: str): # account is IKeyringAccount
        return next((acc for acc in self.accounts if acc.get_address().lower() == address.lower()), None)

    def remove_account(self, account): # account is IKeyringAccount
        self.accounts = [acc for acc in self.accounts if acc != account] # orig. == account

# rings.simple_keyring

class SimpleKeyring:

    account = None #IKeyringAccount;
    network: KeyringNetwork.Constellation.value #KeyringNetwork

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
        self.network = data.get("network")
        #self.account = keyringRegistry.createAccount(data.get("network")).deserialize(data.get("accounts")[0])
        self.account = DagAccount().deserialize(data.get("accounts")[0])

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