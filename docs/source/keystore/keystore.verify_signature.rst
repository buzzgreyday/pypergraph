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

    valid_signature = KeyStore().verify_data(public_key="e123...", encoded_msg="...", signature="f123...")

    if not valid_signature:
        print("Invalid signature.")
    else:
        print("Valid signature.")

