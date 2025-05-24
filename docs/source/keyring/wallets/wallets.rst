Wallets
=======

This wallet is a hierarchical deterministic wallet type.
This wallet type has a keyrings variable with a list of the created ``HdKeyring`` objects.

Multi Chain Wallet
------------------

**Parameters**

+--------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| **Parameter**| **Type**                                             | **Description**                                                                             |
+==============+======================================================+=============================================================================================+
| private_key  | ``str``                                              | The private key used for signing, in hexadecimal format.                                    |
+--------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| msg          | ``dict``                                             | Custom Metagraph data to be signed.                                                         |
+--------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| prefix       | ``bool`` (default ``True``), ``False``, or ``str``   | Determines whether to prepend a signature prefix. If ``True``, the default prefix is used;  |
|              |                                                      | if a custom string is provided, it is prepended; if ``False``, no prefix is added.          |
+--------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+
| encoding     | ``None`` (default), ``"base64"``, or custom function | The encoding to apply to the message. Use ``"base64"`` for base64 encoding or provide a     |
|              |                                                      | custom function.                                                                            |
+--------------+------------------------------------------------------+---------------------------------------------------------------------------------------------+

.. admonition:: Default Prefix
   :class: note

   Setting the parameter ``prefix=True`` will prepend ``"\u0019Constellation Signed Data:\n"`` along with the message length to the encoded message before serialization. Setting it to ``False`` will omit the prefix, and providing a custom string will use that string as the prefix.

**Example Usage**

.. code-block:: python

    # Required imports
    import time
    import json
    import base64

    from pypergraph import KeyStore

    # Sample data to sign
    water_and_energy_usage = {
        "address": "from_address_value",
        "energyUsage": {
            "usage": 7,
            "timestamp": int(time.time() * 1000),
        },
        "waterUsage": {
            "usage": 7,
            "timestamp": int(time.time() * 1000),
        },
    }

    # Custom encoding function example
    def encode(data: dict) -> str:
        return json.dumps(data, separators=(',', ':'))

    # Generate a signature and hash for the custom data
    signature, hash_value = KeyStore().data_sign(
        private_key="f123...",
        msg=water_and_energy_usage,
        prefix=False,
        encoding=encode
    )


.. dropdown:: Lifecycle
   :animate: fade-in

   .. code-block:: python

       from typing import Union, Optional, Callable, Tuple, Literal
       import hashlib
       import json
       import base64
       import time

       from cryptography.hazmat.backends import default_backend
       from cryptography.hazmat.primitives import hashes
       from cryptography.hazmat.primitives.asymmetric import ec
       from cryptography.hazmat.primitives.asymmetric.utils import (
           decode_dss_signature,
           encode_dss_signature,
           Prehashed
       )

       from pypergraph.core.constants.SECP256K1_ORDER

       class KeyStore:
           DATA_SIGN_PREFIX = "\u0019Constellation Signed Data:\n"

           def encode_data(
               self,
               msg: dict,
               prefix: Union[bool, str] = True,
               encoding: Optional[Union[Literal["base64"], Callable[[dict], str], None]] = None,
           ) -> str:
               """
               Encode the message using the provided encoding method.
               """
               if encoding:
                   if callable(encoding):
                       msg = encoding(msg)
                   elif encoding == "base64":
                       encoded = json.dumps(msg, separators=(",", ":"))
                       msg = base64.b64encode(encoded.encode()).decode()
                   else:
                       raise ValueError("KeyStore :: Not a valid encoding method.")
               else:
                   msg = json.dumps(msg, separators=(",", ":"))

               if prefix is True:
                   msg = f"{self.DATA_SIGN_PREFIX}{len(msg)}\n{msg}"
               elif isinstance(prefix, str):
                   msg = f"{prefix}{len(msg)}\n{msg}"
               return msg

           def data_sign(
               self,
               private_key: str,
               msg: dict,
               prefix: Union[bool, str] = True,
               encoding: Optional[Union[Literal["base64"], Callable[[dict], str], None]] = None,
           ) -> Tuple[str, str]:
               """
               Encode, serialize, and sign custom Metagraph data.
               Returns a tuple of (signature, hash).
               """
               # Encode the data
               msg_encoded = self.encode_data(msg=msg, prefix=prefix, encoding=encoding)
               # Serialize the message
               serialized = msg_encoded.encode("utf-8")
               # Generate SHA-256 hash of the serialized data
               hash_ = hashlib.sha256(serialized).hexdigest()
               # Sign the hash using the sign method
               signature = self.sign(private_key, hash_)
               return signature, hash_

           @staticmethod
           def sign(private_key: str, msg: str) -> str:
            """
            Create transaction signature using the `cryptography` library.

            :param private_key: Private key in hex format.
            :param msg: Transaction message (string).
            :return: Canonical DER signature in hex.
            """

            # Convert hex private key to cryptography object
            private_key_bytes = bytes.fromhex(private_key)
            private_key_int = int.from_bytes(private_key_bytes, byteorder='big')
            private_key = ec.derive_private_key(
                private_key_int, ec.SECP256K1(), default_backend()
            )

            # Prehash message with SHA-512 and truncate to 32 bytes
            msg_digest = hashlib.sha512(msg.encode("utf-8")).digest()[:32]

            # Sign deterministically (RFC 6979) and enforce canonical form
            signature = private_key.sign(
                msg_digest,
                ec.ECDSA(Prehashed(hashes.SHA256())))  # Prehashed for raw digest

            # Decode signature to (r, s) and enforce canonical `s`
            r, s = decode_dss_signature(signature)
            if s > SECP256K1_ORDER // 2:
                s = SECP256K1_ORDER - s

            # Re-encode as canonical DER signature
            canonical_signature = encode_dss_signature(r, s)
            return canonical_signature.hex()



       # Example usage of data signing
       water_and_energy_usage = {
           "address": "from_address_value",
           "energyUsage": {
               "usage": 7,
               "timestamp": int(time.time() * 1000),
           },
           "waterUsage": {
               "usage": 7,
               "timestamp": int(time.time() * 1000),
           },
       }

       def encode(data: dict) -> str:
           return json.dumps(data, separators=(',', ':'))

       signature, hash_value = KeyStore().data_sign(
           private_key="f123...",
           msg=water_and_energy_usage,
           prefix=False,
           encoding=encode
       )
