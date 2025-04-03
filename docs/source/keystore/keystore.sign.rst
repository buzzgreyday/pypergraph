Sign
====

-----

Currency Transaction
--------------------

The process begins by hashing the transaction hash using SHA-512. Next, the private key (provided in hexadecimal format) is converted into a signing key using the secp256k1 curve. Then, employing a deterministic signing method (akin to RFC6979), the first 32 bytes of the hash are signed. Finally, the signature is adjusted to enforce canonical form and encoded in DER format before being returned.

**Parameters**

+--------------+-----------------+----------------------------------------------------------------------------+
| **Parameter**| **Type**        | **Description**                                                            |
+==============+=================+============================================================================+
| private_key  | ``str``         | The private key used for signing, in hexadecimal format.                   |
+--------------+-----------------+----------------------------------------------------------------------------+
| msg          | ``str``         | Message or transaction hash generated during transaction preparation.      |
+--------------+-----------------+----------------------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    # Required imports
    import hashlib
    from ecdsa import SigningKey, SECP256k1, sigencode_der
    from pyasn1.codec.der.encoder import encode as der_encode
    from pyasn1.codec.der.decoder import decode as der_decode
    from pyasn1.type.univ import Sequence, Integer

    from pypergraph import KeyStore

    # Generate a signature for a transaction
    signature = KeyStore().sign(private_key="e123...", msg="f123...")


.. dropdown:: Lifecycle
   :animate: fade-in

   .. code-block:: python

       from typing import Union, Optional, Callable, Tuple
       import hashlib
       import json
       import base64

       from ecdsa import SigningKey, SECP256k1, sigencode_der
       from pyasn1.codec.der.encoder import encode as der_encode
       from pyasn1.codec.der.decoder import decode as der_decode
       from pyasn1.type.univ import Sequence, Integer

       class KeyStore:
           DATA_SIGN_PREFIX = "\u0019Constellation Signed Data:\n"

           @staticmethod
           def sign(private_key: str, msg: str) -> str:

               SECP256K1_ORDER = SECP256k1.order

               def _enforce_canonical_signature(signature: bytes) -> bytes:
                   r, s = _decode_der(signature)
                   if s > SECP256K1_ORDER // 2:
                       s = SECP256K1_ORDER - s
                   return _encode_der(r, s)

               def _decode_der(signature: bytes):
                   seq, _ = der_decode(signature, asn1Spec=Sequence())
                   r = int(seq[0])
                   s = int(seq[1])
                   return r, s

               def _encode_der(r: int, s: int) -> bytes:
                   seq = Sequence()
                   seq.setComponentByPosition(0, Integer(r))
                   seq.setComponentByPosition(1, Integer(s))
                   return der_encode(seq)

               def _sign_deterministic_canonical(private_key: str, msg: bytes) -> str:
                   sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
                   signature_der = sk.sign_digest_deterministic(
                       msg[:32],
                       hashfunc=hashlib.sha256,
                       sigencode=sigencode_der,
                   )
                   canonical_signature_der = _enforce_canonical_signature(signature_der)
                   return canonical_signature_der.hex()

               msg_bytes = hashlib.sha512(msg.encode("utf-8")).digest()
               return _sign_deterministic_canonical(private_key=private_key, msg=msg_bytes)

       # Example usage of signing a transaction
       signature = KeyStore().sign(private_key="e123...", msg="f123...")


-----

Data
----

Custom Metagraph data is signed using the same method as for transaction signing, with differences in message serialization and encoding. By default, the transaction ``value`` is taken as the ``msg`` parameter. In addition to JSON encoding, the system supports ``base64`` encoding or injection of custom encoding functions and prefixes.

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

       from ecdsa import SigningKey, SECP256k1, sigencode_der
       from pyasn1.codec.der.encoder import encode as der_encode
       from pyasn1.codec.der.decoder import decode as der_decode
       from pyasn1.type.univ import Sequence, Integer

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

               SECP256K1_ORDER = SECP256k1.order

               def _enforce_canonical_signature(signature: bytes) -> bytes:
                   r, s = _decode_der(signature)
                   if s > SECP256K1_ORDER // 2:
                       s = SECP256K1_ORDER - s
                   return _encode_der(r, s)

               def _decode_der(signature: bytes):
                   seq, _ = der_decode(signature, asn1Spec=Sequence())
                   r = int(seq[0])
                   s = int(seq[1])
                   return r, s

               def _encode_der(r: int, s: int) -> bytes:
                   seq = Sequence()
                   seq.setComponentByPosition(0, Integer(r))
                   seq.setComponentByPosition(1, Integer(s))
                   return der_encode(seq)

               def _sign_deterministic_canonical(private_key: str, msg: bytes) -> str:
                   sk = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
                   signature_der = sk.sign_digest_deterministic(
                       msg[:32],
                       hashfunc=hashlib.sha256,
                       sigencode=sigencode_der,
                   )
                   canonical_signature_der = _enforce_canonical_signature(signature_der)
                   return canonical_signature_der.hex()

               msg_bytes = hashlib.sha512(msg.encode("utf-8")).digest()
               return _sign_deterministic_canonical(private_key=private_key, msg=msg_bytes)

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

---

Personal Message
----------------

**Parameters**

+--------------+-----------------+---------------------------------------------------------+
| **Parameter**| **Type**        | **Description**                                         |
+==============+=================+=========================================================+
| private_key  | ``str``         | The private key used for signing, in hexadecimal format.|
+--------------+-----------------+---------------------------------------------------------+
| msg          | ``str``         | Message to sign.                                        |
+--------------+-----------------+---------------------------------------------------------+

.. admonition:: Personal Sign Prefix
   :class: note

   Prepends ``"\u0019Constellation Signed Message:\n"`` to the message before signing with private key.


.. code-block:: python

    from pypergraph import KeyStore

    signature = KeyStore().personal_sign(msg="...", private_key="f123...")
