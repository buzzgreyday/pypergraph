from pypergraph.dag_keyring import SingleAccountWallet, MultiChainWallet, Encryptor

# TODO: EVERYTHING NEEDS A CHECK. Manager has more methods than the ones below. This is only enough to create new wallets. We also need e.g. storage.
class KeyringManager:
    def __init__(self):
        self.encryptor = Encryptor()
        # self.storage =
        self.wallets = []
        self.password = ""

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
        #this.updateMemStoreWallets();
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
        #await self.storage.set('vault', encryptedString);