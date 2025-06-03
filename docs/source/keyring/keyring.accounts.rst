Keyring Accounts
================

Accounts contain methods for deriving keys, etc. Besides the default ``dag_account`` and ``eth_account`` modules,
the ``accounts`` sub-package also contain the an asset library. This can be used to add additional token support (see,
:doc:`asset library </keyring/keyring.accounts.asset_library>`

All accounts are based on the abstract class ``EcdsaAccount`` (Pydantic model). New account classes can inherit from
this base model. Right now, new account custom account types can be used by adding them to the account registry.

**Add account to registry**

.. code-block:: python

   from pypergraph.keyring import account_registry, MultiAccountWallet()
   import CustomAccount # Your custom account that inherits from pypergraph.keyring.accounts.ecdsa_account.EcdsaAccount

    account_registry.add_account("Custom", CustomAccount)

    wallet = MultiAccountWallet()
    wallet.create(network="Custom", label="New Custom", mnemonic="abandon abandon abandon ...", num_of_accounts=3)
