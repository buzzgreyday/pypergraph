Verify Signatures
=================

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

        from ecdsa import SECP256k1, VerifyingKey
        from ecdsa.util import sigdecode_der

        def verify(public_key: str, msg: str, signature: str) -> bool:
            """
            Verify is the signature is valid.

            :param public_key:
            :param msg: Hex format
            :param signature:
            :return: True or False
            """
            msg = hashlib.sha512(msg.encode("utf-8")).digest()
            vk = VerifyingKey.from_string(bytes.fromhex(public_key), curve=SECP256k1)
            try:
                # Use verify_digest for prehashed input
                valid = vk.verify_digest(
                    bytes.fromhex(signature),
                    msg[:32],  # Prehashed hash
                    sigdecode=sigdecode_der,
                )
                return valid
            except Exception:
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

