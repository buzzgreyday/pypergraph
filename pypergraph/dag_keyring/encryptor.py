import os
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from base64 import b64encode, b64decode


class Encryptor:

    async def encrypt(self, password: str, data) -> str:
        salt = self.generate_salt()

        password_derived_key = self.key_from_password(password, salt)
        payload = self.encrypt_with_key(password_derived_key, data)
        payload["salt"] = salt

        return json.dumps(payload)

    async def decrypt(self, password: str, text: json):
        payload = json.loads(text) if isinstance(text, str) else text
        salt = payload["salt"]
        key = self.key_from_password(password, salt)

        return self.decrypt_with_key(key, payload)

    def encrypt_with_key(self, key: bytes, data) -> dict:
        text = str(data).replace("'", "\"")
        print("Data to be encrypted", text)
        data_bytes = text.encode("utf-8")
        iv = os.urandom(16)

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data_bytes) + encryptor.finalize()

        return {
            "data": b64encode(ciphertext).decode("utf-8"),
            "iv": b64encode(iv).decode("utf-8"),
            "tag": b64encode(encryptor.tag).decode("utf-8")
        }

    def decrypt_with_key(self, key: bytes, payload: dict):
        try:
            encrypted_data = b64decode(payload["data"])
            iv = b64decode(payload["iv"])
            tag = b64decode(payload["tag"])
        except KeyError as e:
            raise ValueError(f"Missing field in payload: {e}")
        except Exception as e:
            raise ValueError(f"Invalid payload: {e}")

        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()

        try:
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            print("Decrypted data:" , decrypted_data.decode("utf-8").replace("'", "\""))
        except Exception as e:
            raise ValueError("Decryption failed: Invalid tag or corrupted data.") from e
        return json.loads(decrypted_data.decode("utf-8").replace("'", "\""))

    @staticmethod
    def key_from_password(password: str, salt: str, iterations: int = 100_000) -> bytes:
        """
        Derives a secure key from a password and a hexadecimal salt using PBKDF2.

        Args:
            password (str): The password to derive the key from.
            salt (str): A hexadecimal string representing the salt.
            iterations (int): The number of iterations for the PBKDF2 function.

        Returns:
            bytes: The derived cryptographic key.
        """
        # Convert hex salt to bytes
        try:
            salt_bytes = bytes.fromhex(salt)
        except ValueError:
            raise ValueError("Invalid hexadecimal salt provided.")

        # Use PBKDF2 to derive the key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256 requires a 32-byte key
            salt=salt_bytes,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode("utf-8"))

    def generate_salt(self, byte_count: int = 32) -> str:
        return os.urandom(byte_count).hex()
