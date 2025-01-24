from pyee.asyncio import AsyncIOEventEmitter

from pypergraph.dag_core import KeyringWalletType
from pypergraph.dag_keyring import SingleAccountWallet, MultiChainWallet, Encryptor
from pypergraph.dag_keyring.bip import Bip39Helper

from pypergraph.dag_keyring.storage import StateStorageDb, ObservableStore


# TODO: EVERYTHING NEEDS A CHECK. Manager has more methods than the ones below. This is only enough to create new wallets and store them
class KeyringManager(AsyncIOEventEmitter):

    def __init__(self):
        super().__init__()
        self.encryptor = Encryptor()
        self.storage = StateStorageDb()
        self.wallets = []
        self.password = ""
        self.mem_store = ObservableStore({"is_unlocked": False, "wallets": []})
        # KeyringManager is also an event emitter
        self.on("new_account", self.new_multi_chain_hd_wallet)
        self.on("remove_account", self.remove_account)

    def is_unlocked(self):
        return bool(self.password)

    async def clear_wallets(self):
        """Clear wallet cahce."""

        self.wallets = []
        self.mem_store.update_state({ "wallets": [] })

    @staticmethod
    def generate_mnemonic():
        return Bip39Helper().generate_mnemonic()

    def create_multi_chain_hd_wallet(self, label: str, seed: str = ""):
        """
        After validating password and seed phrase and deleting wallet cache, this is the next step in creating or restoring a wallet, by default.

        :param label: Wallet name.
        :param seed: Seed phrase.
        :return:
        """

        wallet = MultiChainWallet()
        label = label or "Wallet #" + f"{len(self.wallets) + 1}"
        # Create the multichain wallet from a seed phrase.
        wallet.create(label, seed)
        # Save safe wallet values in the manager cache
        # Secret values are encrypted and stored (default: encrypted JSON)
        self.wallets.append(wallet)
        self.full_update()
        return wallet

    async def create_or_restore_vault(self, label: str, seed: str, password: str):
        """
        First step, creating or restoring a wallet.
        This is the default wallet type when creating a new wallet.

        :param label: The name of the wallet.
        :param seed: Seed phrase.
        :param password: A string of characters.
        :return:
        """

        if not password:
            raise ValueError("KeyringManager :: A password is required to create or restore a Vault.")
        elif type(password) != str:
            raise ValueError("KeyringManager :: Password has invalid format.")
        else:
            # Set the password to be associated with the wallet.
            self.password = password

        if len(label) > 12 or type(label) != str:
            raise ValueError("KeyringManager :: Label must be a string below 12 characters.")

        if type(seed) != str:
            raise ValueError(f"KeyringManager :: A seed phrase must be a string, got {type(seed)}.")
        if seed:
            if len(seed.split(' ')) not in (12, 24):
                raise ValueError("KeyringManager :: The seed phrase must be 12 or 24 words long.")
            if not Bip39Helper().is_valid(seed):
                raise ValueError(f"KeyringManager :: The seed phrase is invalid.")

        # Starts fresh
        await self.clear_wallets()
        wallet = self.new_multi_chain_hd_wallet(label, seed)
        await self.full_update()

        return wallet

    # creates a single wallet with one chain, creates first account by default, one per chain.
    async def create_single_account_wallet(self, label: str, network, private_key: str):

        wallet = SingleAccountWallet()
        label = label or "Wallet #" + f"{len(self.wallets) + 1}"

        wallet.create(network, private_key, label)
        self.wallets.append(wallet)

        await self.full_update()

        return wallet


    async def full_update(self):

        await self.persist_all_wallets(self.password)
        await self.update_mem_store_wallets()
        self.notify_update()

    async def persist_all_wallets(self, password):
        password = password or self.password
        if not password or type(password) != str:
            raise ValueError("KeyringManager :: Password is not a valid string.")

        self.password = password

        s_wallets = [w.serialize() for w in self.wallets]

        encrypted_string = await self.encryptor.encrypt(self.password, { "wallets": s_wallets })

        await self.storage.set("vault", encrypted_string)

    async def update_mem_store_wallets(self):
        wallets = [w.get_state() for w in self.wallets]
        self.mem_store.update_state({"wallets": wallets})

    def set_password(self, password):
        self.password = password

    def set_wallet_label(self, wallet_id: str, label: str):
        self.get_wallet_by_id(wallet_id).set_label(label)

    def get_wallet_by_id(self, id: str):
        wallet = None
        for w in self.wallets:
            if w.id == id:
                return wallet
        raise ValueError(f"KeyringManager :: No wallet found with the id: " + id)

    def get_accounts(self):
        return [account for wallet in self.wallets for account in wallet.get_accounts()]

    def check_password(self, password):
        return bool(self.password == password)

    def notify_update(self):
        self.emit("update", self.mem_store.get_state())

    async def logout(self):

        # Reset ID counter that used to enumerate wallet IDs. \
        [w.reset_sid() for w in self.wallets]
        self.password = None
        self.mem_store.update_state({ "is_unlocked": False })
        await self.clear_wallets()
        self.emit('lock')
        self.notify_update()

    async def login(self, password: str):
        self.wallets = await self.unlock_wallets(password)
        self.update_unlocked()
        self.notify_update()

    async def unlock_wallets(self, password: str):
        encrypted_vault = await self.storage.get("vault")
        if not encrypted_vault:
            # Support recovering wallets from migration
            self.password = password
            return []

        await self.clear_wallets()
        vault = await self.encryptor.decrypt(password, encrypted_vault) # VaultSerialized
        self.password = password
        self. wallets = [await self._restore_wallet(w) for w in vault["wallets"]]
        print("Wallets after restore:", self.mem_store.get_state())
        await self.update_mem_store_wallets()
        print("Wallets after memory update", self.mem_store.get_state())
        return self.wallets

    def update_unlocked(self):
        self.mem_store.update_state({"is_unlocked": True})
        self.emit("unlock")

    async def _restore_wallet(self, w_data): # KeyringSerialized
        print()
        print()
        if w_data["type"] == KeyringWalletType.MultiChainWallet.value:
            print("w_data MCW:", w_data)
            wallet = MultiChainWallet()
            wallet.deserialize(w_data)

        elif w_data["type"] == KeyringWalletType.SingleAccountWallet.value:
            wallet = SingleAccountWallet()
            wallet.deserialize(w_data)

        # else if (wData.type === KeyringWalletType.MultiAccountWallet) {
        # wallet = new MultiAccountWallet();
        # wallet.deserialize(wData);
        # }
        # else if (wData.type == = KeyringWalletType.MultiKeyWallet) {
        # wallet = new MultiKeyWallet();
        # wallet.deserialize(wData);
        # }
        else:
            raise ValueError("KeyringManager :: Unknown Wallet type - " + w_data.type + ", support types are [" + KeyringWalletType.MultiChainWallet.value + "," + KeyringWalletType.SingleAccountWallet.value + "]")

        self.wallets.append(wallet)

        return wallet
