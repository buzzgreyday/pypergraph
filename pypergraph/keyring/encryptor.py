import asyncio
import json
import secrets
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import hmac as crypto_hmac
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
import argon2

_executor = ThreadPoolExecutor(max_workers=4)  # Adjust as needed

class SecurityConstants:
    """Cryptographic parameters meeting wallet security standards"""
    AES_KEY_SIZE = 32  # 256-bit
    ARGON_TIME_COST = 3  # OWASP recommended minimum
    ARGON_MEMORY_COST = 65536  # 64MB per hash
    ARGON_PARALLELISM = 1
    SALT_SIZE = 32  # 256-bit salt
    NONCE_SIZE = 12  # 96-bit nonce for GCM
    HMAC_KEY_SIZE = 32
    VERSION = 1


class AsyncAesGcmEncryptor:
    def __init__(self):
        self.version = SecurityConstants.VERSION

    async def encrypt(self, password: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Securely encrypt wallet data using:
        - Argon2id for memory-hard KDF
        - AES-256-GCM for authenticated encryption
        - HKDF for key separation
        - Random nonce with HMAC integrity
        """
        salt = secrets.token_bytes(SecurityConstants.SALT_SIZE)
        nonce = secrets.token_bytes(SecurityConstants.NONCE_SIZE)

        # Async key derivation
        encryption_key, hmac_key = await self._derive_keys(password, salt)

        # Encrypt data
        aesgcm = AESGCM(encryption_key)
        plaintext = json.dumps(data).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Build and sign vault
        vault = {
            "version": self.version,
            "ciphertext": ciphertext.hex(),
            "salt": salt.hex(),
            "nonce": nonce.hex(),
            "hmac": "",
            "kdf_params": {
                "algorithm": "argon2id",
                "time_cost": SecurityConstants.ARGON_TIME_COST,
                "memory_cost": SecurityConstants.ARGON_MEMORY_COST,
                "parallelism": SecurityConstants.ARGON_PARALLELISM
            }
        }

        vault["hmac"] = (await self._calculate_hmac(hmac_key, vault)).hex()
        return vault

    async def decrypt(self, password: str, vault: Dict[str, Any]) -> Dict[str, Any]:
        """Secure decryption with full validation"""
        await self._validate_vault(vault)

        salt = bytes.fromhex(vault["salt"])
        nonce = bytes.fromhex(vault["nonce"])
        ciphertext = bytes.fromhex(vault["ciphertext"])
        stored_hmac = bytes.fromhex(vault["hmac"])

        # Derive keys async
        encryption_key, hmac_key = await self._derive_keys(password, salt)

        # Verify HMAC before decryption
        if not secrets.compare_digest(
                await self._calculate_hmac(hmac_key, vault),
                stored_hmac
        ):
            raise SecurityException("HMAC validation failed")

        # Decrypt data
        try:
            aesgcm = AESGCM(encryption_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            return json.loads(plaintext.decode())
        except InvalidTag:
            raise SecurityException("Authentication failed")

    async def _derive_keys(self, password: str, salt: bytes) -> tuple[bytes, bytes]:
        """Memory-hard key derivation with Argon2id + HKDF"""
        loop = asyncio.get_running_loop()

        # Argon2id in executor (CPU-bound)
        raw_hash = await loop.run_in_executor(
            _executor,
            argon2.low_level.hash_secret_raw,
            password.encode(),
            salt,
            SecurityConstants.ARGON_TIME_COST,
            SecurityConstants.ARGON_MEMORY_COST,
            SecurityConstants.ARGON_PARALLELISM,
            SecurityConstants.AES_KEY_SIZE + SecurityConstants.HMAC_KEY_SIZE,
            argon2.Type.ID,
        )

        # HKDF for key separation
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=SecurityConstants.AES_KEY_SIZE + SecurityConstants.HMAC_KEY_SIZE,
            salt=salt,
            info=b"wallet-key-derivation",
            backend=default_backend()
        )
        expanded_key = await loop.run_in_executor(None, hkdf.derive, raw_hash)

        return (
            expanded_key[:SecurityConstants.AES_KEY_SIZE],
            expanded_key[SecurityConstants.AES_KEY_SIZE:]
        )

    async def _calculate_hmac(self, key: bytes, vault: Dict[str, Any]) -> bytes:
        """HMAC over critical vault parameters"""
        h = crypto_hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
        h.update(vault["salt"].encode())
        h.update(vault["nonce"].encode())
        h.update(vault["ciphertext"].encode())
        h.update(json.dumps(vault["kdf_params"]).encode())
        return await asyncio.get_event_loop().run_in_executor(None, h.finalize)

    async def _validate_vault(self, vault: Dict[str, Any]):
        """Structural and version validation"""
        if vault.get("version") != self.version:
            raise SecurityException("Unsupported version")

        required = ["ciphertext", "salt", "nonce", "hmac", "kdf_params"]
        if any(field not in vault for field in required):
            raise SecurityException("Missing required fields")


class SecurityException(Exception):
    pass


# Usage Example
async def main():
    encryptor = AsyncAesGcmEncryptor()
    sensitive_data = {
        "private_key": "0x...",
        "wallet_address": "0x...",
        "balance": "100 ETH"
    }

    # Encrypt
    vault = await encryptor.encrypt("SuperSecretPassword123!", sensitive_data)
    print("Encrypted Vault:", json.dumps(vault, indent=2))

    # Decrypt
    try:
        decrypted = await encryptor.decrypt("SuperSecretPassword123!", vault)
        print("Decrypted Data:", decrypted)
    except SecurityException as e:
        print(f"Security Alert: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())