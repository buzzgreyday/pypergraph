Verify Signature
================

-----

Transaction Signature Verification
----------------------------------

**Parameters**

+--------------------+----------+-------------------------------------------------------+
| **Parameter**      | **Type** | **Description**                                       |
+====================+==========+=======================================================+
| public_key         | ``str``  | Public keys as hexadecimal string.                    |
+--------------------+----------+-------------------------------------------------------+
| msg                | ``str``  | Message used to verify the signature with public key. |
+--------------------+----------+-------------------------------------------------------+
| signature          | ``str``  | Signature to be verified with public key and message. |
+--------------------+----------+-------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph import KeyStore

    valid_signature = KeyStore().verify(public_key="e123...", msg="...", signature="f123...")

    if not valid_signature:
        print("Invalid signature.")
    else:
        print("Valid signature.)

.. dropdown:: Lifecycle
   :animate: fade-in

    .. code-block:: python

        import hashlib

        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
        from cryptography.exceptions import InvalidSignature

        @staticmethod
        def verify(public_key: str, msg: str, signature: str) -> bool:
            """
            Verify is the signature is valid.

            :param public_key:
            :param msg: Hex format
            :param signature:
            :return: True or False
            """
            # TODO
            # Compute SHA512 digest of the hex string's UTF-8 bytes and truncate
            sha512_digest = hashlib.sha512(msg.encode("utf-8")).digest()[:32]
            print(public_key)
            # Step 2: Load public key from hex
            public_key_bytes = bytes.fromhex(public_key)
            if len(public_key_bytes) == 65:
                public_key_bytes = public_key_bytes[1:] # Remove 04
            if len(public_key_bytes) != 64:
                raise ValueError("Public key must be 64 bytes (uncompressed SECP256k1).")

            # Split into x and y coordinates (32 bytes each)
            x = int.from_bytes(public_key_bytes[:32], byteorder="big")
            y = int.from_bytes(public_key_bytes[32:], byteorder="big")

            # Create public key object
            public_numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256K1())
            public_key = public_numbers.public_key(default_backend())

            # Step 3: Verify the signature
            try:
                public_key.verify(
                    bytes.fromhex(signature),
                    sha512_digest,
                    ec.ECDSA(Prehashed(hashes.SHA256()))  # Treat digest as SHA256-sized
                )
                return True
            except InvalidSignature:
                return False

-----

Data Signature Verification
---------------------------

**Parameters**

+----------------+----------+------------------------------------------------------------+
| **Parameters** | **Type** | **Description**                                            |
+================+==========+============================================================+
| public_key     | ``str``  | Public keys as hexadecimal string.                         |
+----------------+----------+------------------------------------------------------------+
| encoded_msg    | ``str``  | Message used to verify the signature with public key.      |
|                |          | Important: Encode the message according to the             |
|                |          | method used when signing the data.                         |
+----------------+----------+------------------------------------------------------------+
| signature      | ``str``  | Signature to be verified with public key and message.      |
+----------------+----------+------------------------------------------------------------+

**Example Usage**

.. code-block:: python

    from pypergraph import KeyStore()

    import time
    import json

    from pypergraph import KeyStore

    pk = KeyStore.get_private_key_from_mnemonic("abandon ...")
    pub_k = KeyStore.get_public_key_from_private(pk)
    address = KeyStore.get_dag_address_from_public_key(pub_k)

    # Sample data to sign
    water_and_energy_usage = {
        "address": address,
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
        private_key=pk,
        msg=water_and_energy_usage,
        prefix=False,
        encoding=encode
    )

    # Same encoding as used to sign
    encoded_msg = encode(water_and_energy_usage)
    valid_signature = KeyStore().verify_data(public_key=pub_k, encoded_msg=encoded_msg, signature=signature)

    if not valid_signature:
        print("Invalid signature.")
    else:
        print("Valid signature.")

