Manage Keys
===========

The keyring package has a class KeyringManager() which handles encryption, decryption and storage of wallet data and secrets.

-----

Create or Restore Vault
-----------------------

The default method for creating or restoring a Hierarchical Deterministic wallet. This method will create or restore a vault with a
Multi Chain Wallet (MCW) based on the parameters ``password`` and ``seed``. One keyring per chain.

**Parameters**

+--------------+-------------------+----------------------------------------------------------------------------+
|**Parameter** | **Type**          | **Description**                                                            |
+==============+===================+============================================================================+
| password     | ``str``           | Used to encrypt the vault.                                                 |
+--------------+-------------------+----------------------------------------------------------------------------+
| seed         | ``str``: 12 word  | Used to derive the Constellation and Ethereum private keys from hd path.   |
|              | mnemonic seed     | BIP index 0 only.                                                          |
+--------------+-------------------+----------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")

    vault = await key_manager.create_or_restore_vault(password="super_S3cretP_Asswo0rd", seed=mnemo)

.. dropdown:: Lifecycle
   :animate: fade-in

   .. code-block:: python

    from pypergraph.keyring.wallets.multi_chain_wallet import MultiChainWallet
    from pypergraph.core.cross_platform.state_storage_db import StateStorageDb
    from pypergraph.keyring.storage.observable_store import ObservableStore
    from pypergraph.keyring.bip_helpers.bip39_helper import Bip39Helper
    from pypergraph.keyring import Encryptor


    class KeyringManager:

        def __init__(self, storage_file_path: Optional[str] = None):
            super().__init__()
            self.encryptor: Encryptor = Encryptor()
            self.storage: StateStorageDb = StateStorageDb(file_path=storage_file_path)
            self.wallets: List[Union[MultiChainWallet, MultiKeyWallet, MultiAccountWallet, SingleAccountWallet]] = []
            self.password: Optional[str] = None
            self.mem_store: ObservableStore = ObservableStore()
            # Reactive state management

        # Ignoring som lines of code...

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
            # await self._full_update()
            return wallet

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")

    vault = await key_manager.create_or_restore_vault(password="super_S3cretP_Asswo0rd", seed=mnemo)

The wallet creation method above creates a hierarchical deterministic wallet from the ``MultiChainWallet`` class.
This default wallet class is a Pydantic model. The wallet ``id``, ``label``, list of ``HdKeyring`` objects and the mnemonic phrase unencrypted in memory.
See :doc:`keyring wallet types </keyring/wallets/wallets>` for more detail.

-----

Create Single Account Wallet
----------------------------

The default method for creating non-HD wallet. Creates a single wallet with one chain, first account index by default.
One keyring account per chain. The Single Account Wallet (SAW) is saved to vault.

**Parameters**

+--------------+-------------------+----------------------------------------------------------------------------+
|**Parameter** | **Type**          | **Description**                                                            |
+==============+===================+============================================================================+
| label        | ``str``           | Used to encrypt the vault.                                                 |
+--------------+-------------------+----------------------------------------------------------------------------+
| private_key  | ``str``: 12 word  | Used to derive the Constellation and Ethereum private keys from hd path.   |
+--------------+-------------------+----------------------------------------------------------------------------+
| network      | ``str``           | Can be ``Constellation`` or ``Ethereum``.                                  |
+--------------+-------------------+----------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager
    from pypergraph.keystore import KeyStore

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    key_manager.set_password("super_S3cretP_Asswo0rd")
    pk = KeyStore.get_private_key_from_mnemonic("abandon abandon abandon ...")
    wallet = await key_manager.create_single_account_wallet(label="New SAW", private_key=pk)
    await key_manager.logout()

See :doc:`keyring wallet types </keyring/wallets/wallets>` for more detail.

-----

Manager Login
-------------

Returns decrypted wallets from encrypted vault.

**Parameters**

+--------------+-------------------+----------------------------------------------------------------------------+
|**Parameter** | **Type**          | **Description**                                                            |
+==============+===================+============================================================================+
| password     | ``str``           | Used to decrypt the vault.                                                 |
+--------------+-------------------+----------------------------------------------------------------------------+
