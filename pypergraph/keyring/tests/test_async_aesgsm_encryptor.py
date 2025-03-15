import pytest
import secrets
from pypergraph.keyring.encryptor import AsyncAesGcmEncryptor, SecurityException  # Adjust import based on your file structure


@pytest.mark.asyncio
async def test_encryption_decryption():
    """Ensures that encrypted data can be correctly decrypted."""
    encryptor = AsyncAesGcmEncryptor()
    password = "SuperSecretPassword!"
    data = {"private_key": "0x123456789", "wallet_address": "0xabcdef"}

    # Encrypt & Decrypt
    vault = await encryptor.encrypt(password, data)
    decrypted_data = await encryptor.decrypt(password, vault)

    assert decrypted_data == data, "Decrypted data should match original"


@pytest.mark.asyncio
async def test_hmac_integrity_check():
    """Ensures that HMAC prevents tampered data from being decrypted."""
    encryptor = AsyncAesGcmEncryptor()
    password = "SecurePassword123!"
    data = {"account": "secure_wallet", "balance": "100ETH"}

    vault = await encryptor.encrypt(password, data)

    # Modify ciphertext (simulating an attacker modifying encrypted data)
    vault["ciphertext"] = secrets.token_hex(len(vault["ciphertext"]) // 2)

    with pytest.raises(SecurityException, match="HMAC validation failed"):
        await encryptor.decrypt(password, vault)


@pytest.mark.asyncio
async def test_incorrect_password():
    """Ensures decryption fails with an incorrect password."""
    encryptor = AsyncAesGcmEncryptor()
    correct_password = "CorrectPassword!"
    wrong_password = "WrongPassword!"
    data = {"seed_phrase": "random words for wallet"}

    vault = await encryptor.encrypt(correct_password, data)

    with pytest.raises(SecurityException, match="HMAC validation failed"):
        await encryptor.decrypt(wrong_password, vault)


@pytest.mark.asyncio
async def test_vault_structure_validation():
    """Ensures vault validation rejects malformed vaults."""
    encryptor = AsyncAesGcmEncryptor()
    password = "AnotherSecurePassword!"
    data = {"data": "important"}

    vault = await encryptor.encrypt(password, data)

    # Remove a required field
    del vault["nonce"]

    with pytest.raises(SecurityException, match="Missing required fields"):
        await encryptor.decrypt(password, vault)


@pytest.mark.asyncio
async def test_version_mismatch():
    """Ensures that an outdated or incompatible vault version is rejected."""
    encryptor = AsyncAesGcmEncryptor()
    password = "SecurePass123!"
    data = {"wallet": "my_wallet"}

    vault = await encryptor.encrypt(password, data)
    vault["version"] = 99  # Fake an unsupported version

    with pytest.raises(SecurityException, match="Unsupported version"):
        await encryptor.decrypt(password, vault)


@pytest.mark.asyncio
async def test_corrupt_vault_data():
    """Ensures that corrupted vault data triggers security exceptions."""
    encryptor = AsyncAesGcmEncryptor()
    password = "TopSecret!"
    data = {"some_key": "some_value"}

    vault = await encryptor.encrypt(password, data)

    # Corrupting the vault fields
    vault["ciphertext"] = "zzzz"  # Invalid hex
    with pytest.raises(ValueError):
        await encryptor.decrypt(password, vault)


@pytest.mark.asyncio
async def test_large_data_encryption():
    """Ensures large data encryption works properly."""
    encryptor = AsyncAesGcmEncryptor()
    password = "LongPassphrase!"
    large_data = {"data": "X" * 10000}  # 10,000-character string

    vault = await encryptor.encrypt(password, large_data)
    decrypted_data = await encryptor.decrypt(password, vault)

    assert decrypted_data == large_data, "Large data should decrypt correctly"


@pytest.mark.asyncio
async def test_multiple_encryptions_different_nonces():
    """Ensures that encrypting the same data twice produces different nonces and ciphertexts."""
    encryptor = AsyncAesGcmEncryptor()
    password = "SecurePass"
    data = {"message": "Hello, world!"}

    vault1 = await encryptor.encrypt(password, data)
    vault2 = await encryptor.encrypt(password, data)

    assert vault1["ciphertext"] != vault2["ciphertext"], "Ciphertext should be unique per encryption"
    assert vault1["nonce"] != vault2["nonce"], "Nonce should be random per encryption"


@pytest.mark.asyncio
async def test_edge_case_empty_data():
    """Ensures empty dictionaries can be encrypted and decrypted correctly."""
    encryptor = AsyncAesGcmEncryptor()
    password = "EdgeCaseTest!"
    data = {}

    vault = await encryptor.encrypt(password, data)
    decrypted_data = await encryptor.decrypt(password, vault)

    assert decrypted_data == data, "Empty data should decrypt correctly"

