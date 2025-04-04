.. pypergraph documentation master file, created by
   sphinx-quickstart on Sun Jan  5 16:50:08 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pypergraph: Python SDK for Constellation Network
================================================

Pypergraph is a Python tool similar to `DAG for JavaScript (DAG4JS) <https://github.com/StardustCollective/dag4.js/>`_.
Use it to send data to Metagraph, build a wallet and more.

.. caution::

  This package is currently in alpha. Changes will happen rapidly, as I develop.
  **Do not use it for production purposes** as it may contain bugs, security issues and incomplete features.

  **Wish to contribute?** Please reach out on `GitHub <https://github.com/buzzgreyday>`_.

.. toctree::
   :maxdepth: 1
   :caption: Getting Started:

   getting_started/getting_started.overview
   getting_started/getting_started.installation

.. toctree::
   :maxdepth: 1
   :caption: Account:

   account/account.introduction
   account/account.keys
   account/account.network
   account/account.transactions
   account/account.other

.. toctree::
   :maxdepth: 1
   :caption: Network:

   network/network.introduction
   network/network.configuration
   network/network.dag_token_network
   network/network.metagraph_token_network
   network/network.rest_api_clients

.. toctree::
   :maxdepth: 1
   :caption: Keystore:

   keystore/keystore.introduction
   keystore/keystore.keys
   keystore/keystore.sign
   keystore/keystore.verify_signature
