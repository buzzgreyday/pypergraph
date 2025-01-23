import asyncio
from pyee.asyncio import AsyncIOEventEmitter

from pypergraph.dag_keyring import SingleAccountWallet, MultiChainWallet, Encryptor


class ObservableStore:
    def __init__(self, initial_state: dict):
        self._state = initial_state
        self._observers = []

    def get_state(self):
        return self._state

    def update_state(self, new_state: dict):
        self._state = new_state
        self.notify_observers()

    def subscribe(self, callback):
        self._observers.append(callback)

    def notify_observers(self):
        for observer in self._observers:
            observer(self._state)


class KeyringVault:
    def __init__(self, password: str, encryptor: Encryptor):
        # Initialize the encrypted observable store
        self.mem_store = ObservableStore({"is_unlocked": False, "wallets": []})
        self.encryptor = encryptor
        self.password = password

    def add_wallet(self, wallet: str):
        """Encrypt and add a wallet to the state."""
        encrypted_wallet = self.encryptor.encrypt(self.password, wallet)
        current_state = self.mem_store.get_state()

        updated_wallets = current_state["wallets"] + [encrypted_wallet]
        self.mem_store.update_state({**current_state, "wallets": updated_wallets})

    def get_wallets(self):
        """Decrypt and retrieve all wallets."""
        current_state = self.mem_store.get_state()
        return [
            self.encryptor.decrypt(self.password, encrypted_wallet)
            for encrypted_wallet in current_state["wallets"]
        ]

    def unlock(self, password: str) -> bool:
        """Unlock the vault."""
        if password == self.password:
            current_state = self.mem_store.get_state()
            self.mem_store.update_state({**current_state, "is_unlocked": True})
            return True
        return False

    def lock(self):
        """Lock the vault."""
        current_state = self.mem_store.get_state()
        self.mem_store.update_state({**current_state, "is_unlocked": False})

# TODO: EVERYTHING NEEDS A CHECK. Manager has more methods than the ones below. This is only enough to create new wallets. We also need e.g. storage.
class KeyringManager(AsyncIOEventEmitter):

    def __init__(self):
        super().__init__()
        self.encryptor = Encryptor()
        # self.storage =
        self.wallets = []
        self.password = ""
        self.mem_store = ObservableStore({"is_unlocked": False, "wallets": []})
        self.on("new_single_account", self.create_single_account_wallet)  # Bind event here

    def is_unlocked(self):
        return bool(self.password)

    def clear_wallets(self):
        self.wallets = []
        # this.memStore.updateState({
        #     wallets: [],
        # })

    def new_multi_chain_hd_wallet(self, label: str, seed: str):
        wallet = MultiChainWallet()
        label = label or 'Wallet #' + f"{len(self.wallets) + 1}"
        wallet.create(label, seed)
        self.wallets.append(wallet)
        return wallet

    async def create_or_restore_vault(self, label: str, seed: str, password: str):

        if not password:
            raise ValueError("KeyringManager :: A password is required to create or restore a Vault.")
        elif type(password) != str:
            raise ValueError("KeyringManager :: Password has invalid format.")
        else:
            self.password = password

        if not seed:
            raise ValueError("KeyringManager :: A seed is required to create or restore a Vault.")
        # TODO: Validate seed
        # new Error('Seed phrase is invalid.')

        self.clear_wallets()
        wallet = self.new_multi_chain_hd_wallet(label, seed)
        await self.full_update()

        return wallet

    # creates a single wallet with one chain, creates first account by default, one per chain.
    async def create_single_account_wallet(self, label: str, network, private_key: str):

        wallet = SingleAccountWallet()
        label = label or 'Wallet #' + f"{len(self.wallets) + 1}"

        wallet.create(network, private_key, label)
        self.wallets.append(wallet)

        # this.emit('newAccount', wallet.getAccounts()[0]);

        await self.full_update()

        return wallet


    async def full_update(self):

        await self.persist_all_wallets(self.password)
        self.update_mem_store_wallets()
        #this.notifyUpdate();
        #}

    async def persist_all_wallets(self, password):
        password = password or self.password
        if type(password) != str:
            raise ValueError('KeyringManager :: Password is not a string')

        self.password = password

        s_wallets = [w.serialize() for w in self.wallets]

        encryptedString = await self.encryptor.encrypt(self.password, { "wallets": s_wallets })

        # TODO: Add storage
        decryptedString = await self.encryptor.decrypt(self.password, encryptedString)
        print(decryptedString)
        #await self.storage.set('vault', encryptedString);

    def update_mem_store_wallets(self):
        wallets = [w.get_state() for w in self.wallets]
        self.mem_store.update_state({"wallets": wallets})
        print(self.mem_store.get_state())

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return bool(self.password == password)