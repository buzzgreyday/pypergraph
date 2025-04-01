import asyncio
import re
from typing import Optional, Union, List

from rx.subject import BehaviorSubject, Subject

from pypergraph.core import KeyringWalletType, NetworkId
from pypergraph.keyring import Encryptor

from pypergraph.core.cross_platform.state_storage_db import StateStorageDb
from .storage.observable_store import ObservableStore
from .accounts.dag_account import DagAccount
from .accounts.eth_account import EthAccount
from .bip_helpers.bip39_helper import Bip39Helper
from .wallets.multi_account_wallet import MultiAccountWallet
from .wallets.multi_chain_wallet import MultiChainWallet
from .wallets.multi_key_wallet import MultiKeyWallet
from .wallets.single_account_wallet import SingleAccountWallet



class KeyringManager:

    def __init__(self, storage_file_path: Optional[str] = None):
        super().__init__()
        self.encryptor: Encryptor = Encryptor()
        self.storage: StateStorageDb = StateStorageDb(file_path=storage_file_path)
        self.wallets: List[Union[MultiChainWallet, MultiKeyWallet, MultiAccountWallet, SingleAccountWallet]] = []
        self.password: Optional[str] = None
        self.mem_store: ObservableStore = ObservableStore()
        # Reactive state management
        self._state_subject = BehaviorSubject(self.mem_store.get_state())
        self._event_subject = Subject()

    def is_unlocked(self) -> bool:
        return bool(self.password)

    async def clear_wallets(self):
        """Clear wallet cache."""

        self.wallets = []
        self.mem_store.update_state(wallets=[])

    @staticmethod
    def generate_mnemonic() -> str:
        bip39 = Bip39Helper()
        return bip39.generate_mnemonic()

    async def create_multi_chain_hd_wallet(
            self, label: Optional[str] = None, seed: Optional[str] = None
    ) -> MultiChainWallet:
        """
        This is the next step in creating or restoring a wallet, by default.

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
        await self._full_update()
        return wallet

    async def create_or_restore_vault(
            self, password: str, label: Optional[str] = None, seed: Optional[str] = None
    ) -> MultiChainWallet:
        """
        First step, creating or restoring a wallet.
        This is the default wallet type when creating a new wallet.

        :param label: The name of the wallet.
        :param seed: Seed phrase.
        :param password: A string of characters.
        :return:
        """
        bip39 = Bip39Helper()
        self.set_password(password)

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
        await self._full_update()
        return wallet

    # creates a single wallet with one chain, creates first account by default, one per chain.
    async def create_single_account_wallet(
            self, label: str, private_key: str,
            network: Optional[Union[NetworkId.Constellation.value, NetworkId.Ethereum.value]] = None
    ) -> SingleAccountWallet:

        wallet = SingleAccountWallet()
        label = label or "Wallet #" + f"{len(self.wallets) + 1}"

        wallet.create(network=network, private_key=private_key, label=label)
        self.wallets.append(wallet)

        await self._full_update()

        return wallet


    async def _full_update(self):

        await self._persist_all_wallets(self.password)
        await self._update_mem_store_wallets()
        self._notify_update()

    async def _persist_all_wallets(self, password):
        password = password or self.password

        self.set_password(password)

        s_wallets = [w.model_dump() for w in self.wallets]

        encrypted_string = await self.encryptor.encrypt(self.password, { "wallets": s_wallets })

        await self.storage.set("vault", encrypted_string)

    async def _update_mem_store_wallets(self):
        wallets = [w.get_state() for w in self.wallets]
        self.mem_store.update_state(wallets=wallets)

    def set_password(self, password: str):
        """Will enforce basic restrictions on password creation"""

        if len(password) < 8:
            raise ValueError("KeyringManager :: Password must be at least 8 characters long.")
        if re.search(r'\d', password) is None:
            raise ValueError("KeyringManager :: Password must contain at least one number.")
        if re.search(r'[a-z]', password) is None:
            raise ValueError("KeyringManager :: Password must contain at least one lowercase letter.")
        if re.search(r'[A-Z]', password) is None:
            raise ValueError("KeyringManager :: Password must contain at least one uppercase letter.")

        self.password = password

    def set_wallet_label(self, wallet_id: str, label: str):
        self.get_wallet_by_id(wallet_id).set_label(label)

    def get_wallet_by_id(
            self, id: str
    ) -> Union[MultiChainWallet, SingleAccountWallet, MultiAccountWallet, MultiKeyWallet]:
        for w in self.wallets:
            if w.id == id:
                return w
        raise ValueError("KeyringManager :: No wallet found with the id: " + id)

    def get_accounts(self) -> List[Union[DagAccount, EthAccount]]:
        return [account for wallet in self.wallets for account in wallet.get_accounts()]

    async def remove_account(self, address):
        wallet_for_account = self.get_wallet_for_account(address)
        wallet_for_account.remove_account()
        self._event_subject.on_next({"type": "removed_account", "data": address})
        accounts = wallet_for_account.get_accounts()
        if len(accounts) == 0:
            self.remove_empty_wallets()
        await self._persist_all_wallets(password=self.password)
        await self._update_mem_store_wallets()
        self._notify_update()

    def remove_empty_wallets(self):
        self.wallets = [keyring for keyring in self.wallets if len(keyring.get_accounts()) > 0]

    def get_wallet_for_account(
            self, address: str
    ) -> Union[MultiChainWallet, SingleAccountWallet, MultiAccountWallet, MultiKeyWallet]:
        winner = next(
            (keyring for keyring in self.wallets if any(a.get_address() == address for a in keyring.get_accounts())),
            None
        )
        if winner:
            return winner
        raise ValueError('KeyringManager :: No keyring found for the requested account.')


    def check_password(self, password) -> bool:
        return bool(self.password == password)

    def _notify_update(self):
        current_state = self.mem_store.get_state()
        self._state_subject.on_next(current_state)
        self._event_subject.on_next({"type": "state_update", "data": current_state})

    async def logout(self):

        # Reset ID counter that used to enumerate wallet IDs. \
        [w.reset_sid() for w in self.wallets]
        self.password = None
        self.mem_store.update_state(is_unlocked=False)
        await self.clear_wallets()
        self._event_subject.on_next({"type": "lock"})
        self._notify_update()

    async def login(self, password: str):
        self.wallets = await self._unlock_wallets(password)
        self._update_unlocked()
        self._notify_update()

    async def _unlock_wallets(
            self, password: str
    ) -> List[Union[MultiChainWallet, SingleAccountWallet, MultiAccountWallet, MultiKeyWallet]]:
        encrypted_vault = await self.storage.get("vault")
        if not encrypted_vault:
            # Support recovering wallets from migration
            self.set_password(password)
            return []

        await self.clear_wallets()
        vault = await self.encryptor.decrypt(password, encrypted_vault) # VaultSerialized
        self.password = password
        tasks = [self._restore_wallet(w) for w in vault["wallets"]]
        self.wallets = [w for w in await asyncio.gather(*tasks, return_exceptions=True) if not isinstance(w, Exception)]
        await self._update_mem_store_wallets()
        return self.wallets

    def _update_unlocked(self):
        self.mem_store.update_state(is_unlocked=True)
        self._state_subject.on_next(self.mem_store.get_state())
        self._event_subject.on_next({"type": "unlock"})


    async def _restore_wallet(
            self, data
    ) -> Union[MultiChainWallet, SingleAccountWallet, MultiAccountWallet, MultiKeyWallet]: # KeyringSerialized
        if data["type"] == KeyringWalletType.MultiChainWallet.value:
            ## Can export secret (mnemonic) but cant remove or import
            wallet = MultiChainWallet()
            # Create keyrings
            wallet.deserialize(
                label=data["label"], secret=data["secret"], rings=data["rings"]
            )

        elif data["type"] == KeyringWalletType.SingleAccountWallet.value:
            ## Can export secret (private key) but not remove or import account
            wallet = SingleAccountWallet()
            # Create keyrings
            wallet.deserialize(
                network=data["network"], label=data["label"], secret=data["secret"])

        elif data["type"] == KeyringWalletType.MultiAccountWallet.value:
            ## This can export secret key (mnemonic), remove account but not import
            wallet = MultiAccountWallet()
            # Create keyrings
            wallet.deserialize(
                label=data["label"], network=data["network"], secret=data["secret"],
                num_of_accounts=data["num_of_accounts"], rings=data["rings"]
            )
        elif data["type"] == KeyringWalletType.MultiKeyWallet.value:
            ## This can import account but not export secret or remove account
            wallet = MultiKeyWallet()
            # Create keyrings
            wallet.deserialize(label=data["label"], network=data["network"], accounts=data["accounts"])
        else:
            raise ValueError(
                "KeyringManager :: Unknown Wallet type - " + data["type"] + ", support types are ["
                + KeyringWalletType.MultiChainWallet.value + "," + KeyringWalletType.SingleAccountWallet.value + "]"
            )

        self.wallets.append(wallet)

        return wallet
