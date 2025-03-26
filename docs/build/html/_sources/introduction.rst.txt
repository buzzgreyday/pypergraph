Overview
========

.. caution::

  The package is currently in alpha.

  **Wish to contribute?** Please reach out on `GitHub <https://github.com/buzzgreyday>`_.


Pypergraph consists of 5 subpackages.

1. The :doc:`account package </pypergraph.account>` handles account functionality such as creation and storage of keys, logging in and out, connecting to networks and Metagraphs, transfer of currency and data, etc.


2. The :doc:`keystore package </pypergraph.keystore>` handles key related functionalities such as currency and data transaction signing/verification, encrypting and decrypting, key generation and validation.


3. The :doc:`network package </pypergraph.network>` handles network related functionalities such as network and Metagraph configuration and get/post methods for CN APIs.


4. The :doc:`keyring package </pypergraph.keyring>` contains a :code:`KeyringManager()` that handles wallet creation, restoration and secure storage of wallet accounts and data using the :code:`AsyncAesGcmEncryptor`. Used together with above packages it enables easy building of e.g. wallet applications.


5. The :doc:`core package </pypergraph.core>` contains the :code:`REST API client` and the shared modules :code:`constants` and :code:`exceptions`.

