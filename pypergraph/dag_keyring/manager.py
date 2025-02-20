from typing import Optional

from pyee.asyncio import AsyncIOEventEmitter

from pypergraph.dag_core import KeyringWalletType
from pypergraph.dag_keyring import SingleAccountWallet, MultiChainWallet, Encryptor, MultiKeyWallet, MultiAccountWallet
from pypergraph.dag_keyring.bip import Bip39Helper

from pypergraph.dag_keyring.storage import StateStorageDb, ObservableStore


# TODO: EVERYTHING NEEDS A CHECK. Manager has more methods than the ones below. This is only enough to create new wallets and store them
class KeyringManager(AsyncIOEventEmitter):

    def __init__(self):
        super().__init__()
        self.encryptor = Encryptor()
        self.storage = StateStorageDb()
        self.wallets = []
        self.password: Optional[str] = None  # Use None instead of an empty string
        self.mem_store = ObservableStore({"is_unlocked": False, "wallets": []}) # Memory storage
        # KeyringManager is also an event emitter
        self.on("new_account", self.create_multi_chain_hd_wallet)
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

    async def create_multi_chain_hd_wallet(self, label: Optional[str] = None, seed: Optional[str] = None) -> MultiChainWallet:
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
        print(wallet)
        # Save safe wallet values in the manager cache
        # Secret values are encrypted and stored (default: encrypted JSON)
        self.wallets.append(wallet)
        await self.full_update()
        return wallet

    async def create_or_restore_vault(self, password: str, label: Optional[str] = None, seed: Optional[str] = None) -> MultiChainWallet:
        """
        First step, creating or restoring a wallet.
        This is the default wallet type when creating a new wallet.

        :param label: The name of the wallet.
        :param seed: Seed phrase.
        :param password: A string of characters.
        :return:
        """
        bip39 = Bip39Helper()
        if not password:
            raise ValueError("KeyringManager :: A password is required to create or restore a Vault.")
        elif type(password) is not str:
            raise ValueError("KeyringManager :: Password has invalid format.")
        else:
            # Set the password to be associated with the wallet.
            self.password = password

        if type(seed) not in (str, None):
            raise ValueError(f"KeyringManager :: A seed phrase must be a string, got {type(seed)}.")
        if seed:
            if len(seed.split(' ')) not in (12, 24):
                raise ValueError("KeyringManager :: The seed phrase must be 12 or 24 words long.")
            if not bip39.is_valid(seed):
                raise ValueError("KeyringManager :: The seed phrase is invalid.")

        # Starts fresh
        await self.clear_wallets()
        wallet = await self.create_multi_chain_hd_wallet(label, seed)
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
        if not password or type(password) is not str:
            raise ValueError("KeyringManager :: Password is not a valid string.")

        self.password = password

        s_wallets = [w.model_dump() for w in self.wallets]

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
        for w in self.wallets:
            if w.id == id:
                return w
        raise ValueError("KeyringManager :: No wallet found with the id: " + id)

    def get_accounts(self):
        return [account for wallet in self.wallets for account in wallet.get_accounts()]

    async def remove_account(self, address):
        wallet_for_account = self.get_wallet_for_account(address)

        wallet_for_account.remove_account(address)
        self.emit('removed_account', address)
        accounts = wallet_for_account.get_accounts()

        if len(accounts) == 0:
            self.remove_empty_wallets()

        await self.persist_all_wallets(password=self.password)
        await self.update_mem_store_wallets()
        self.notify_update()

    def remove_empty_wallets(self):
        self.wallets = [keyring for keyring in self.wallets if len(keyring.get_accounts()) > 0]

    def get_wallet_for_account(self, address: str):
        winner = next(
            (keyring for keyring in self.wallets if any(a.get_address() == address for a in keyring.get_accounts())),
            None
        )
        if winner:
            return winner
        ValueError('KeyringManager :: No keyring found for the requested account.')


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
        await self.update_mem_store_wallets()
        return self.wallets

    def update_unlocked(self):
        self.mem_store.update_state({"is_unlocked": True})
        self.emit("unlock")

    async def _restore_wallet(self, w_data): # KeyringSerialized
        if w_data["type"] == KeyringWalletType.MultiChainWallet.value:
            ## Can export secret (mnemonic) but cant remove or import
            wallet = MultiChainWallet()
            wallet.deserialize(w_data)

        elif w_data["type"] == KeyringWalletType.SingleAccountWallet.value:
            ## Can export secret (private key) but not remove or import account
            wallet = SingleAccountWallet()
            wallet.deserialize(w_data)

        elif w_data["type"] == KeyringWalletType.MultiAccountWallet.value:
            ## This can export secret key (mnemonic), remove account but not import
            wallet = MultiAccountWallet()
            wallet.deserialize(w_data)
        elif w_data["type"] == KeyringWalletType.MultiKeyWallet.value:
            ## This can import account but not export secret or remove account
            wallet = MultiKeyWallet()
            wallet.deserialize(w_data)
        else:
            raise ValueError("KeyringManager :: Unknown Wallet type - " + w_data.type + ", support types are [" + KeyringWalletType.MultiChainWallet.value + "," + KeyringWalletType.SingleAccountWallet.value + "]")

        self.wallets.append(wallet)

        return wallet
