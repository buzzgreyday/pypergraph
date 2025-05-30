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

The above method will automatically login. Required to handle wallets.

-----

Login
-----

Login is required to access the encrypted wallets. This method decrypts wallets and updates the state storage database found here (see: ``core.cross_platform.state_storage_db.py``).
Different storage methods can be injected into ``StateStorageDB``, default is JSON (see: ``core.cross_platform.di.json_storage.py``).

**Parameters**

+--------------+-------------------+----------------------------------------------------------------------------+
|**Parameter** | **Type**          | **Description**                                                            |
+==============+===================+============================================================================+
| password     | ``str``           | Used to decrypt the vault.                                                 |
+--------------+-------------------+----------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    await key_manager.login("super_S3cretP_Asswo0rd")
    key_manager.get_wallet_for_account("DAG1...")
    await key_manager.logout()

-----

After logging in the following methods can be used.

-----

Logout
------

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    await key_manager.login("super_S3cretP_Asswo0rd")
    await key_manager.logout()

.. dropdown:: Lifecycle
   :animate: fade-in

   .. code-block:: python

        async def logout(self):

            # Reset ID counter that used to enumerate wallet IDs. \
            [w.reset_sid() for w in self.wallets]
            self.password = None
            self.mem_store.update_state(is_unlocked=False)
            await self.clear_wallets()
            self._event_subject.on_next({"type": "lock"})
            self._notify_update()

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

See :doc:`keyring wallet types </keyring/wallets/wallets>` for more detail.

-----

Get Accounts
------------

Returns a list of all accounts for all wallets.

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    key_manager.login("super_S3cretP_Asswo0rd")
    accounts = key_manager.get_accounts()

-----

Get Wallet for Account
----------------------

Returns the wallet matching the address provided.

**Parameters**

+--------------+-------------------+----------------------------------------------------------------------------+
|**Parameter** | **Type**          | **Description**                                                            |
+==============+===================+============================================================================+
| address      | ``str``           | DAG or ETH address.                                                        |
+--------------+-------------------+----------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    key_manager.login("super_S3cretP_Asswo0rd")
    wallet = key_manager.get_wallet_for_account("DAG1...")

-----

Get Wallet by ID
----------------

Returns the wallet matching the wallet ID.

**Parameters**

+--------------+-------------------+----------------------------------------------------------------------------+
|**Parameter** | **Type**          | **Description**                                                            |
+==============+===================+============================================================================+
| id           | ``str``           | The wallet identifier, e.g. ``MCW1``                                       |
+--------------+-------------------+----------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    key_manager.login("super_S3cretP_Asswo0rd")
    wallet = key_manager.get_wallet_by_id("MCW1")

-----

Set Wallet Label
----------------

Change the wallet label of a wallet by its ID.

**Parameters**

+--------------+-------------------+----------------------------------------------------------------------------+
|**Parameter** | **Type**          | **Description**                                                            |
+==============+===================+============================================================================+
| wallet_id    | ``str``           | The wallet identifier, e.g. ``MCW1``                                       |
+--------------+-------------------+----------------------------------------------------------------------------+
| label        | ``str``           | The wallet label, e.g. ``Jane Doe's Wallet``                               |
+--------------+-------------------+----------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    key_manager.login("super_S3cretP_Asswo0rd")
    key_manager.set_wallet_label("Jane Doe's Wallet")

-----

Remove Account
--------------

Removes the account matching the address from vault and memory.

**Parameters**

+--------------+-------------------+----------------------------------------------------------------------------+
|**Parameter** | **Type**          | **Description**                                                            |
+==============+===================+============================================================================+
| address      | ``str``           | DAG or ETH address.                                                        |
+--------------+-------------------+----------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    key_manager.login("super_S3cretP_Asswo0rd")
    await key_manager.remove_account("DAG1...")

.. dropdown:: Lifecycle
   :animate: fade-in

   .. code-block:: python

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

-----

Check Password
--------------

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    key_manager.login("super_S3cretP_Asswo0rd")
    is_valid = await key_manager.check_password("super_S3cretP_Asswo0rd")

-----

Set Password
------------

**Example Usage**

.. code-block:: python

    from pypergraph.keyring import KeyringManager

    key_manager = KeyringManager(storage_file_path="/path/to/key_storage.json")
    key_manager.login("super_S3cretP_Asswo0rd")
    key_manager.set_password("NewPassword=123")
    is_valid = await key_manager.check_password("super_S3cretP_Asswo0rd")
