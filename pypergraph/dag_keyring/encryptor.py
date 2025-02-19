
from base64 import b64encode, b64decode

import os
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding


class Encryptor:
    def __init__(self, iterations: int = 100000):
        self.iterations = iterations
        self.algorithm = "aes-256-cbc"
        self.digest = "sha256"

    async def encrypt(self, password: str, data: dict) -> dict:
        salt = os.urandom(16)
        iv = os.urandom(16)

        # Derive encryption key
        key = self._derive_key(password, salt)

        # Prepare and encrypt data
        encrypted_data = self._encrypt(key, iv, json.dumps(data))

        return {
            "data": encrypted_data.hex(),
            "iv": iv.hex(),
            "salt": salt.hex(),
            "iterations": self.iterations,
            "digest": self.digest,
            "algorithm": self.algorithm
        }

    async def decrypt(self, password: str, vault: dict) -> dict:
        # Convert hex values to bytes
        salt = bytes.fromhex(vault["salt"])
        iv = bytes.fromhex(vault["iv"])
        encrypted_data = bytes.fromhex(vault["data"])

        # Verify algorithm compatibility
        if vault["algorithm"] != self.algorithm:
            raise ValueError("Unsupported encryption algorithm")
        if vault["digest"] != self.digest:
            raise ValueError("Unsupported digest algorithm")

        # Derive encryption key
        key = self._derive_key(password, salt, vault["iterations"])

        # Decrypt and return data
        decrypted_data = self._decrypt(key, iv, encrypted_data)
        return json.loads(decrypted_data)

    def _derive_key(self, password: str, salt: bytes, iterations: int = None) -> bytes:
        """PBKDF2 key derivation"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations or self.iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))

    def _encrypt(self, key: bytes, iv: bytes, plaintext: str) -> bytes:
        """AES-256-CBC encryption with PKCS7 padding"""
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext.encode('utf-8')) + padder.finalize()

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        return encryptor.update(padded_data) + encryptor.finalize()

    def _decrypt(self, key: bytes, iv: bytes, ciphertext: bytes) -> str:
        """AES-256-CBC decryption with PKCS7 padding removal"""
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        return plaintext.decode('utf-8')
