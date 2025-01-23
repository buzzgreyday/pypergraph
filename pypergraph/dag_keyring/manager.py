import asyncio
from pyee.asyncio import AsyncIOEventEmitter

from pypergraph.dag_core import KeyringWalletType
from pypergraph.dag_keyring import SingleAccountWallet, MultiChainWallet, Encryptor


class ObservableStore:
    def __init__(self, initial_state: dict):
        self._state = initial_state
        self._observers = []

    def get_state(self):
        return self._state

    def update_state(self, new_state: dict):
        self._state.update(new_state)
        self.notify_observers()

    def subscribe(self, callback):
        self._observers.append(callback)

    def notify_observers(self):
        for observer in self._observers:
            observer(self._state)

# TODO: EVERYTHING NEEDS A CHECK. Manager has more methods than the ones below. This is only enough to create new wallets. We also need e.g. storage.
class KeyringManager(AsyncIOEventEmitter):

    def __init__(self):
        super().__init__()
        self.encryptor = Encryptor()
        self.storage =
        self.wallets = []
        self.password = ""
        self.mem_store = ObservableStore({"is_unlocked": False, "wallets": []})
        self.on("new_single_account", self.create_single_account_wallet)  # Bind event here

    def is_unlocked(self):
        return bool(self.password)

    async def clear_wallets(self):
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
        await self.update_mem_store_wallets()
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

    async def update_mem_store_wallets(self):
        wallets = [w.get_state() for w in self.wallets]
        self.mem_store.update_state({"wallets": wallets})
        print("Current Wallet State:", self.mem_store.get_state())

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return bool(self.password == password)

    def notify_update(self):
        self.emit('update', self.mem_store.get_state())

    async def login(self, password: str):
        self.wallets = await self.unlock_wallets(password)
        self.update_unlocked()
        self.notify_update()

    async def unlock_wallets(self, password: str):
        raise NotImplementedError("KeyringManager :: This is not yet implemented.")
        encrypted_vault = await self.storage.get('vault')
        if not encrypted_vault:
            # Support recovering wallets from migration
            self.password = password
            return []

        await self.clear_wallets()
        vault = await self.encryptor.decrypt(password, encrypted_vault) # VaultSerialized
        self.password = password
        self.wallets = [self._restore_wallet(w) for w in vault.wallets]
        await self.update_mem_store_wallets()
        return self.wallets

    def update_unlocked(self):
        self.mem_store.update_state({"is_unlocked": True})
        self.emit('unlock')

    async def _restore_wallet(self, w_data): # KeyringSerialized

        if w_data.type == KeyringWalletType.MultiChainWallet.value:
            wallet = MultiChainWallet()
            wallet.deserialize(w_data)

        elif w_data.type == KeyringWalletType.SingleAccountWallet.value:
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
            raise ValueError('KeyringManager :: Unknown Wallet type - ' + w_data.type + ', support types are [' + KeyringWalletType.MultiChainWallet.value + ',' + KeyringWalletType.SingleAccountWallet.value + ']')

        self.wallets.append(wallet)

        return wallet
