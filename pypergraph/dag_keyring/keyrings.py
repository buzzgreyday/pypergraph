from mnemonic import Mnemonic

from pypergraph.dag_core.constants import KeyringNetwork
from pypergraph.dag_keyring.accounts import EcdsaAccount, DagAccount
from pypergraph.dag_keystore import Bip32


class HdKeyring:

    accounts = [] # type IKeyringAccount[] interface
    hd_path: str = None
    mnemonic: str = None
    extended_key: str = None
    root_key = None # Placeholder for Hierarchical Deterministic SigningKey, VerifyingKey, etc.
    network: str = None # Could be either or

    # Read-only wallet
    @staticmethod
    def create_from_extended_key(extended_key: str, network: KeyringNetwork, number_of_accounts: int):
        # TODO: check _init_from...
        inst = HdKeyring()
        inst.extendedKey = extended_key
        inst._init_from_extended_key(extended_key)
        inst.deserialize( { "network": network, "accounts": inst.create_accounts(number_of_accounts) })
        return inst

    @staticmethod
    def create(mnemonic: str, hd_path: str, network, number_of_accounts: int):
        inst = HdKeyring()
        inst.mnemonic = mnemonic
        inst.hd_path = hd_path
        path_parts = [int(part.strip("'")) for part in inst.hd_path.split("/")[1:]]
        purpose = path_parts[0] + 2 ** 31
        coin_type = path_parts[1] + 2 ** 31
        account = path_parts[2] + 2 ** 31
        change = 0
        index = path_parts[3]
        print(path_parts[1])
        seed_bytes = Mnemonic("english").to_seed(inst.mnemonic)
        inst.root_key = Bip32().get_root_key_from_seed(seed_bytes=seed_bytes)
        #inst._init_from_mnemonic(mnemonic) Refactored
        inst.root_key = inst.root_key.ChildKey(purpose).ChildKey(coin_type).ChildKey(account).ChildKey(change).ChildKey(index)
        inst.deserialize( { "network": network, "accounts": inst.create_accounts(number_of_accounts) })
        print(inst.root_key.PrivateKey().hex())
        return inst

    def getNetwork(self):
        return self.network

    def get_hd_path(self):
        return self.hd_path

    def get_extended_public_key(self):
        if self.mnemonic:
            # TODO: needs a suitable library (needs testing)
            return self.root_key.ExtendedKey().hex()
            # return self.root_key.publicExtendedKey().toString('hex') # This will vary depending on the library

        return self.extended_key

    # Serialize all accounts
    def serialize(self):
        return { "network": self.network, "accounts": [acc.serialize(False) for acc in self.accounts] } # this.accounts.map(a => a.serialize(false))


    def deserialize(self, data: dict):
        if data:
            self.network = data.get("network")
            self.accounts = []
            for d in data.get("accounts"):
                print("Retored wallet:", d)
                account = self.add_account_at(d.get("bip44Index"))
                # TODO: Add ecdsa account and token support
                account.set_tokens(d.get("tokens"))
                self.accounts.append(account)

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
        index = index if index >= 0 else len(self.accounts)

        try:
            if self.accounts[index]:
                ValueError('HdKeyring :: Trying to add an account to an index already populated')
        except IndexError:
            pass

        # TODO: This should be fitted to library
        #account = IKeyringAccount;
        if self.mnemonic:
            private_key = self.root_key.PrivateKey().hex()
            print(private_key)
            # Create account
            #account = {"privateKey": private_key, "bip44Index": index}
            #if self.network.value == KeyringNetwork.Constellation.value:
            #    account = DagAccount().deserialize({ "privateKey": private_key, "bip44Index": index })
            #elif self.network.value == KeyringNetwork.Ethereum.value:
            if self.network == KeyringNetwork.Ethereum.value:
                account = EcdsaAccount().deserialize({ "privateKey": private_key, "bip44Index": index }) # Could also be DAG account should be set dynamically
            elif self.network == KeyringNetwork.Constellation.value:
                account = DagAccount().deserialize({ "privateKey": private_key, "bip44Index": index })
            else:
                raise ValueError(f"HDKeyRing :: network can't be '{self.network}'")


        else:
            public_key = self.root_key.PublicKey()
            # Create account

        #const wallet = child.getWallet();
        #if (this.mnemonic) {
        #  const privateKey = wallet.getPrivateKey().toString('hex');
        #  account = keyringRegistry.createAccount(this.network).deserialize({privateKey, bip44Index: index});
        #} else {
        #  const publicKey = wallet.getPublicKey().toString('hex');
        #  account = keyringRegistry.createAccount(this.network).deserialize({publicKey, bip44Index: index});
        #}

        #self.accounts.append(account)

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

    def create_for_network(self, network, privateKey: str):
        inst = SimpleKeyring()
        inst.network = network
        #inst.account = keyringRegistry.createAccount(network).create(privateKey)
        inst.account = DagAccount().create(privateKey)
        print(DagAccount().create(privateKey).get_state())
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