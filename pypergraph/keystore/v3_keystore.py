import asyncio
import os
import uuid
import hashlib
import json

import eth_keyfile
from eth_hash.backends.pycryptodome import keccak256
from typing_extensions import TypedDict, NotRequired

from concurrent.futures import ThreadPoolExecutor
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from mnemonic import Mnemonic

_executor = ThreadPoolExecutor(max_workers=4)  # Adjust as needed

# Type definitions for type hinting
class KDFParamsPhrase(TypedDict):
    prf: str
    dklen: int
    salt: str
    c: int

class CipherParams(TypedDict):
    iv: str

class CryptoStruct(TypedDict):
    cipher: str
    ciphertext: str
    cipherparams: CipherParams
    kdf: str
    kdfparams: KDFParamsPhrase
    mac: str

class V3Keystore(TypedDict):
    crypto: CryptoStruct
    id: str
    version: int
    meta: NotRequired[str]

ENCRYPT = {
    "cipher": "aes-128-ctr",
    "kdf": "pbkdf2",
    "prf": "hmac-sha256",
    "dklen": 32,
    "c": 262144,
    "hash": hashes.SHA256().name
}

def type_check_jphrase(keystore: V3Keystore) -> bool:
    params = keystore.get("crypto", {}).get("kdfparams")
    if params and "salt" in params and "c" in params and "dklen" in params:
        return True
    raise TypeError("V3Keystore :: Invalid JSON Keystore format.")

def blake256(data: bytes) -> str:
    return hashlib.blake2b(data, digest_size=hashlib.blake2b().digest_size).hexdigest()

async def pbkdf2_async(
    passphrase: bytes,
    salt: bytes,
    iterations: int,
    keylen: int,
    digest: str
) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _executor,
        hashlib.pbkdf2_hmac,
        digest,
        passphrase,
        salt,
        iterations,
        keylen
    )

class V3KeystoreCrypto:
    @staticmethod
    async def encrypt_phrase(phrase: str, password: str) -> V3Keystore:
        if not isinstance(phrase, str) or not isinstance(password, str):
            raise TypeError("V3KeystoreCrypto :: Both phrase and password must be strings.")
        mnemo = Mnemonic("english")
        if not mnemo.check(phrase):
            raise TypeError("V3KeystoreCrypto :: Invalid BIP39 phrase.")

        keystore_id = str(uuid.uuid4())
        salt = os.urandom(32)
        iv = os.urandom(16)
        phrase_bytes = phrase.encode("utf-8")
        password_bytes = password.encode("utf-8")

        # Key derivation
        derived_key = await pbkdf2_async(
            password_bytes,
            salt,
            ENCRYPT["c"],
            ENCRYPT["dklen"],
            ENCRYPT["hash"]
        )

        # AES-128-CTR encryption
        cipher = Cipher(
            algorithms.AES(derived_key[:16]),
            modes.CTR(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(phrase_bytes) + encryptor.finalize()

        # MAC calculation
        mac_data = derived_key[16:32] + ciphertext
        mac = keccak256(mac_data).hex()

        # Build the keystore structure
        return V3Keystore(**{
            "crypto": {
                "cipher": ENCRYPT["cipher"],
                "ciphertext": ciphertext.hex(),
                "cipherparams": {"iv": iv.hex()},
                "kdf": ENCRYPT["kdf"],
                "kdfparams": {
                    "prf": ENCRYPT["prf"],
                    "dklen": ENCRYPT["dklen"],
                    "salt": salt.hex(),
                    "c": ENCRYPT["c"]
                },
                "mac": mac
            },
            "id": keystore_id,
            "version": 3,
            "meta": "stardust-collective/pypergraph"
        })

    @staticmethod
    async def decrypt_phrase(keystore: V3Keystore, password: str) -> str:
        type_check_jphrase(keystore)
        crypto = keystore["crypto"]
        kdfparams = crypto["kdfparams"]

        password_bytes = password.encode("utf-8")
        salt = bytes.fromhex(kdfparams["salt"])
        ciphertext = bytes.fromhex(crypto["ciphertext"])
        iv = bytes.fromhex(crypto["cipherparams"]["iv"])

        # Key derivation
        derived_key = await pbkdf2_async(
            password_bytes,
            salt,
            kdfparams["c"],
            kdfparams["dklen"],
            ENCRYPT["hash"]
        )

        # MAC verification
        mac_data = derived_key[16:32] + ciphertext
        calculated_mac = keccak256(mac_data).hex()
        if calculated_mac != crypto["mac"]:
            raise ValueError("V3KeystoreCrypto :: Invalid password.")
        try:
            # AES decryption
            cipher = Cipher(
                algorithms.AES(derived_key[:16]),
                modes.CTR(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            phrase_bytes = decryptor.update(ciphertext) + decryptor.finalize()

            return phrase_bytes.decode("utf-8")
        except Exception as e:
            raise ValueError(f"V3KeystoreCrypto :: Decryption failed: {str(e)}")

# Example usage
async def main():
    phrase = "legal winner thank year wave sausage worth useful legal winner thank yellow"
    password = "securepassword123"

    # Encryption
    encrypted = await V3KeystoreCrypto.encrypt_phrase(phrase, password)
    print("Encrypted keystore:", json.dumps(encrypted, indent=2))

    # Decryption
    decrypted_eth_keyfile = eth_keyfile.decode_keyfile_json(encrypted, "securepassword123".encode("utf-8"))
    print("ETH Keyfile decrypted phrase:", decrypted_eth_keyfile)
    decrypted = await V3KeystoreCrypto.decrypt_phrase(encrypted, password)
    print("\nDecrypted phrase:", decrypted)

if __name__ == "__main__":
    asyncio.run(main())