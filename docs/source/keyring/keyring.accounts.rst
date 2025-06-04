Keyring Accounts
================

Accounts contain methods for deriving keys, etc. Besides the default ``dag_account`` and ``eth_account`` modules,
the ``accounts`` sub-package also contains an ``EcdsaAccount`` abstract class (Pydantic model).
All accounts are based on the abstract class ``EcdsaAccount``. New custom account classes must inherit from this base model.

**Add Custom Account to Registry**

.. code-block:: python

   from pypergraph.keyring import account_registry, MultiAccountWallet()
   import CustomAccount # Your custom account that inherits from pypergraph.keyring.accounts import EcdsaAccount

    account_registry.add_account("Custom", CustomAccount)

    wallet = MultiAccountWallet()
    wallet.create(network="Custom", label="New Custom", mnemonic="abandon abandon abandon ...", num_of_accounts=3)

    accounts = wallet.get_accounts() # Returns a list of EcdsaAccounts

The ``accounts`` sub-package contains the asset libraries ``DagAssetLibrary`` and ``EthAssetLibrary`` (not fully implemented yet).
These classes inherit from the abstract class ``AssetLibrary``, which can be used to construct custom asset libraries, for
additional token support.

**Add Custom Asset Library to Custom Account**

.. code-block:: python

    from pypergraph.keyring import KeyringAssetInfo

    import CustomAccount
    import CustomAssetLibrary

    custom_asset_library = CustomAssetLibrary()

    token = KeyringAssetInfo(
        id='0xa000000000000000000000000000000000000000',
        address='0xa000000000000000000000000000000000000000',
        label='Custom Token',
        symbol='CUS',
        network='testnet',
        decimals=8
    )

    custom_asset_library.import_token(token)

    custom_account = CustomAccount()

    # Add the imported custom token to the custom account
    custom_account.set_tokens(custom_asset_library.serialize())

The above methods are not restricted to custom object, see below.

-----

.. automodule:: pypergraph.keyring.accounts
   :members:
   :undoc-members:
   :show-inheritance:
